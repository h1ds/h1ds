"""Interface to the summary database.

TODO: currently the sqlite table is created without setting data types for
summary attributes. This is possible because SQLite uses dynamic typing, and
simplifies the codebase. It may be desirable to use the optional type specification in
the table columns -- this would be a field in the SummaryAttribute.

timestamp hack - the timestamp attribute of shot instances often return None, and I'm not sure why, so
the workaround is to grab from backend until I solve the problem

"""
from collections import OrderedDict
from django.db import transaction

from celery import chord, group

from h1ds.models import Shot, Device
from h1ds.utils import get_backend_shot_manager_for_device
from h1ds_summary import TABLE_NAME_TEMPLATE
from h1ds_summary.tasks import get_summary_attribute_data, insert_table_attributes, insert_single_table_attribute, update_table_attributes, update_single_table_attribute
from h1ds_summary import get_summary_cursor
from h1ds_summary.parsers import get_where_from_shot_slug, parse_attr_str, parse_filter_str


INITIAL_TABLE_ATTRIBUTES = (
    ("shot", "MEDIUMINT UNSIGNED PRIMARY KEY"),
    ("timestamp", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
)


class SummaryTable:
    def __init__(self, device):
        """Interface to a summary database table.
        
        Args:
            device - an instance of h1ds.models.Device

        """
        self.device = device
        self.table_name = TABLE_NAME_TEMPLATE.format(device.slug)
        if not self.table_exists():
            self.create_table()

    def create_table(self):
        """Create summary table."""
        from h1ds_summary.models import SummaryAttribute

        cursor = get_summary_cursor()
        summary_attrs = SummaryAttribute.objects.filter(device=self.device).values_list('slug', flat=True)

        table_attrs = ""

        for attr_i, attr in enumerate(INITIAL_TABLE_ATTRIBUTES):
            if attr_i > 0:
                table_attrs += ","
            table_attrs += "{} {}".format(attr[0], attr[1])

        summary_attr_arg = ",".join(summary_attrs)

        if summary_attr_arg:
            table_attrs = ",".join([table_attrs, summary_attr_arg])

        cursor.execute("CREATE TABLE %(table)s (%(attrs)s)" % {'table': self.table_name, 'attrs': table_attrs})

    def update_schema(self, check_dtypes=False, delete_orphans=False):
        """Update table if any summary attributes are missing.

        Keyword arguments:
            check_dtypes (bool) (not yet implemented) - also ensure that dtypes are correct
            delete_orphans (bool) - delete attributes in the summary table which don't
            belong to a SummaryAttribute instance

        """
        if check_dtypes:
            raise NotImplementedError
        from h1ds_summary.models import SummaryAttribute

        table_attrs = self.get_attributes_from_table(filter_initial_attributes=True)
        summary_attrs = SummaryAttribute.objects.filter(device=self.device).values_list('slug', flat=True)

        if delete_orphans:
            for t_attr in table_attrs:
                if not t_attr in summary_attrs:
                    # TODO: provide an interface to delete many at the same time.
                    self.delete_attribute(t_attr)

        for s_attr in summary_attrs:
            if not s_attr in table_attrs:
                self.create_attribute(s_attr)

    def create_attribute(self, summary_attribute):
        """Add summary attribute to table.

        Arguments:
            summary_attribute: a SummaryAttribute instance or slug

        This does nothing if the attribute already exists in the table

        """
        try:
            attr_slug = summary_attribute.slug
        except AttributeError:
            attr_slug = summary_attribute

        if attr_slug in self.get_attributes_from_table():
            return

        cursor = get_summary_cursor()
        cursor.execute("ALTER TABLE {} ADD COLUMN {}".format(self.table_name, attr_slug))

    def delete_attribute(self, attribute_name):
        """Delete attribute from the summary table.

        This does not delete any SummaryAttribute instances.

        Arguments:
            attribute_name (str) - name of the summary table attribute to delete.

        Not yet implemented - SQLite can't delete column, need to create new table, delete old, and rename
        See http://www.sqlite.org/lang_altertable.html
        """

        raise NotImplementedError

    def delete_shot(self, shot_number):
        """Delete shot from summary table.

        Arguments:
            shot_number (int) - shot number.

        """

        cursor = get_summary_cursor()
        cursor.execute("DELETE FROM {} WHERE shot={}".format(self.table_name,  shot_number))

    def get_attributes_from_table(self, filter_initial_attributes=False):
        """Get the attributes of the summary table.

        Keyword arguments:
            filter_initial_attributes (bool) - if True, then exclude attributes in INITIAL_TABLE_ATTRIBUTES

        """
        cursor = get_summary_cursor()
        cursor.execute("PRAGMA table_info({})".format(self.table_name))
        attr_list = [a[1] for a in cursor.fetchall()]

        if filter_initial_attributes:
            for initial_attr in INITIAL_TABLE_ATTRIBUTES:
                attr_list.remove(initial_attr[0])

        return attr_list

    def table_exists(self):
        """Check whether table exists.

        Returns:
            Bool: True if table exists, false if it does not.

        """
        cursor = get_summary_cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{}'".format(self.table_name))
        table = cursor.fetchone()
        return bool(table)

    def regenerate_table(self):
        pass

    def update_shot(self, shot):
        """Update a shot in the table.

        """
        return self.add_shot(shot, update=True)

    def update_table(self, check_all_shots=False):
        """Add missing shots to summary table.

        Keyword arguments:
            check_all_shots (bool) - if False (default) then the scan will
            start at the latest shot and iterate through Shot instances
            until a corresponing shot is found in the summary table.
            If True, all Shot instances will be checked.

        The scan always starts with Device.latest_shot, not necessarily the highest shot number.

        """
        shot_queryset = Shot.objects.filter(number__lte=self.device.latest_shot, device=self.device)

        #TODO, complete

    def add_shot(self, shot, update=False):
        """Add shot to summary database.

        Arguments:
            shot (h1ds.models.Shot or shot number)

        Keyword arguments:
            force_overwrite - if False: If the shot already exists then this will do nothing.
                            - if True - overwrite any existing entries for shot

        """
        if not isinstance(shot, Shot):
            shot = Shot(number=shot, device=self.device)
        new_shot = not self.shot_exists(shot)
        if not update and not new_shot:
            return

        table_attributes = self.get_attributes_from_table(filter_initial_attributes=True)

        if new_shot or not update:
            task_name = insert_table_attributes
        else:
            task_name = update_table_attributes

        # Hack workaround - see notes at top of file
        shot_manager = get_backend_shot_manager_for_device(self.device)
        shot_timestamp = shot_manager().get_timestamp_for_shot(shot.number)

        chord(
            (get_summary_attribute_data.s(self.device.slug, shot.number, a) for a in table_attributes),
            task_name.s(table_name=self.table_name, shot_number=shot.number, shot_timestamp=str(shot_timestamp))
        ).apply_async()

    def shot_exists(self, shot):
        """Check whether or not a shot already exists in the summary datbase.

        Arguments:
            shot - either an instance of h1ds.models.Shot or an integer (shot number)

        Returns:
            bool - True if shot exists in the summary database, False if it does not.

        """
        try:
            shot_number = shot.number
        except AttributeError:
            shot_number = shot

        cursor = get_summary_cursor()
        cursor.execute("SELECT shot from {} WHERE shot={}".format(self.table_name, shot_number))
        return bool(cursor.fetchone())

    def populate_attribute(self, summary_attribute, update=True):
        """Populate all instances of summary_attribute in table.

        Arguments:
            summary_attribute - either an instance of h1ds.models.SummaryAttribute or its slug

        """
        try:
            attr_slug = summary_attribute.slug
        except AttributeError:
            attr_slug = summary_attribute

        shot_queryset = Shot.objects.filter(device=self.device, number__lte=self.device.latest_shot.number)

        if update:
            task_name = update_single_table_attribute
        else:
            task_name = insert_single_table_attribute

        shot_manager = get_backend_shot_manager_for_device(self.device)
        shot_timestamp = shot_manager().get_timestamp_for_shot

        group(
            (task_name.s(self.device.slug, shot.number, shot_timestamp(shot.number), attr_slug) for shot in shot_queryset),
        ).apply_async()

    def update_attribute(self, summary_attribute):
        return self.populate_attribute(summary_attribute)

    def get_latest_shot(self):
        """Get the min of self.device.latest_shot and the max shot number in table.

        Returns:
            min(self.device.latest_shot.number, max_table_shot), or
            None - if there are no entries in the summary table

        """
        max_table_shot = self.get_max_shot()
        if not max_table_shot:
            return None

        return min([self.device.latest_shot.number, max_table_shot])

    def get_max_shot(self):
        """Get the maximum shot number in the database table."""

        cursor = get_summary_cursor()
        cursor.execute("SELECT MAX(shot) FROM {}".format(self.table_name))
        result = cursor.fetchone()[0]
        return result

    def do_query(self, select=['shot', 'timestamp'], where=None, as_dict=True):
        """Simple interface to SQL for given select and where statements

        Keywork arguments:
            select (list)  - list of attributes to select
            where (str)    - optional SQL where statement
            as_dict (bool) - if true then the responses will be returned as list of dicts: [{'attr':value, }, ]

        Returns:
            list of dicts (if as_dict is True)
            raw response from sqlite (if as_dict is False)

        """
        select_str = ",".join(select)
        cursor = get_summary_cursor()
        cursor.execute(
            "SELECT {} FROM {} WHERE {} ORDER BY -shot".format(select_str, self.table_name, where)
        )

        data = cursor.fetchall()
        if as_dict:
            return [OrderedDict(zip(select, row)) for row in data]
        else:
            return data

    def do_query_from_path_components(self, shot_str, attr_str, filter_str, as_dict=True):
        """Do SQL query from the URL API path components.

        Arguments:
            shot_str (str) - shot path component, e.g. "76523-76593"
            attr_str (str) - attribute path component, e.g.: "attr1+attr2"
            filter_str (str) - filter path component, e.g.: "attr1__lt__10"

        Keyword arguments:
            as_dict (bool, default=True) - if true then the responses will be returned as list of dicts: [{'attr':value, }, ]

        Returns:
            list of dicts (if as_dict is True)
            raw response from sqlite (if as_dict is False)

        """

        shot_where = get_where_from_shot_slug(self.device, shot_str)
        if shot_where is None:
            return []
        attr_list = parse_attr_str(self.device, attr_str)
        filter_where = parse_filter_str(filter_str)

        for special_attr in ['timestamp', 'shot']:
            if not special_attr in attr_list:
                attr_list.insert(0, special_attr)

        if filter_where is None:
            where = shot_where
        else:
            where = ' AND '.join([shot_where, filter_where])

        return self.do_query(select=attr_list, where=where, as_dict=as_dict)

    def add_or_update_shot(self, shot_number):
        if self.shot_exists(shot_number):
            self.update_shot(shot_number)
        else:
            self.add_shot(shot_number)
