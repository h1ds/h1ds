import subprocess, shlex, uuid, datetime
from django.db import models, connection
from colorsys import hsv_to_rgb

from h1ds_core.signals import h1ds_signal

# Map the single-character codes stored in the database to user-friendly strings
# for the web interface.
DATATYPE_CHOICES = (
    ('F', 'Float'),
    ('I', 'Integer'),
    ('D', 'Date and time'),
    ('T', 'Text'),
    )
# Return a datetime instance for the specific date string returned by MDSplus
datetimeformatter = lambda x: datetime.datetime.strptime(x.strip(), 
                                                         "%d-%b-%Y %H:%M:%S.%f")
# For each datatype stored in the database, provide a function which converts
# a string representation to the correct python class. 
datatype_python = {
    'F':float,
    'I':int,
    'D':datetimeformatter,
    }
# Map the single-character datatype codes to the strings required to manipulate
# SQL databases (e.g. for creating columns in the compiled table)
datatype_sql = {
    'F':'float',
    'I':'int',
    'D':'datetime',
    }

def remove_att_from_single_table(attr_name, table="summary"):
    cursor=connection.cursor()
    cursor.execute("ALTER TABLE %s DROP COLUMN %s" %(table, attr_name))

def add_attr_value_to_single_table(shot_number, attr_name, 
                                   attr_value, table="summary"):
    """ attr_value should be a string, get it using sqlrep()"""
    cursor=connection.cursor()
    cursor.execute("UPDATE %s SET %s=%s WHERE shot=%d" %(table, attr_name, 
                                                         attr_value, 
                                                         int(shot_number)))

def add_shot_to_single_table(shot_number, table="summary"):
    # just in case shot is already in table...
    delete_shot_from_single_table(int(shot_number), table=table)

    cursor = connection.cursor()
    col_list = ['shot']
    val_list = [str(shot_number)]
    attr_list = SummaryAttribute.objects.all()
    for attr in attr_list:
        try:
            v = attr.get_att_class().objects.get(attribute=attr, shot__shot=shot_number).sqlrep()
        except:
            raise Exception("%s, %d" %(attr.slug, int(shot_number)))
        val_list.append(v)
        col_list.append(attr.slug)
    query = "INSERT INTO %(table)s (%(cols)s) VALUES(%(vals)s)" %{'table':table, 'cols':",".join(col_list), 'vals':",".join(val_list)}
    cursor.execute(query)

def update_attr_single_table(attr_name, attr_type, table="summary"):
    cursor = connection.cursor()
    ## check if attribute already exists.
    cursor.execute("describe %s" %table)
    attr_exists = False
    correct_type = False
    for r in cursor.fetchall():
        if r[0] == attr_name:
            attr_exists = True
            if r[1].startswith(attr_type):
                correct_type = True
    if not attr_exists:
        cursor.execute("ALTER TABLE %s ADD COLUMN %s %s" %(table, attr_name, attr_type))
    elif not correct_type:
        cursor.execute("ALTER TABLE %s MODIFY COLUMN %s %s" %(table, attr_name, attr_type))


def delete_shot_from_single_table(shot_number, table="summary"):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM %s WHERE shot=%d" %(table, shot_number))

def compile_single_table(table="summary"):
    """Create a single sql table with attributes as separate columns.

    Use this table where possible to avoid joining attribute tables for 
    each query."""
    shot_table = 'h1ds_summary_shot'

    cursor = connection.cursor()
    attr_list = SummaryAttribute.objects.all()

    # Because there is a MySQL limit of 61 joins in a query, we split
    # the summary table creation into 2 steps, first making temporary tables
    # with at most n_join attributes, and then joining those temporary tables 
    # together. The attribute limit is therefore n_join*61, given n_join<=61
    # the full limit is 3721.
    n_join = 20

    attr_index = range(len(attr_list))
    step_tables = []
    
    tmp_attr_tables = []

    # create separate attribute tables

    for attr in attr_list:
        tmp_name = 'tmp_'+attr.slug
        tmp_attr_tables.append(tmp_name)
        # remove tmp table if it exists
        try:
            cursor.execute("DROP TABLE %s" %tmp_name)
        except:
            pass
        cursor.execute("CREATE TABLE %(tmp_name)s SELECT shot_id as shot,value as %(val_name)s FROM %(this_table)s WHERE attribute_id=%(att_id)d" %{'tmp_name':tmp_name, 'val_name':attr.slug, 'this_table':attr.get_att_class()._meta.db_table, 'att_id':attr.id})
        cursor.execute("CREATE INDEX si ON %s(shot)" %(tmp_name))

    step_table_attrs = {}
    for attr_step in attr_index[::n_join]:
        step_attrs = attr_list[attr_step:attr_step+n_join]
        step_attr_tables = tmp_attr_tables[attr_step:attr_step+n_join]
        step_tablename = table+str(attr_step)
        step_tables.append(step_tablename)
        step_table_attrs[step_tablename] = [a.slug for a in step_attrs]

        # remove tmp table if it exists
        try:
            cursor.execute("DROP TABLE %s" %step_tablename)
        except:
            pass


        attr_tables = ' '.join(["INNER JOIN %(att_table)s ON %(shot_tbl)s.shot=%(att_table)s.shot" %{'att_table':a, 'shot_tbl':shot_table} for a in step_attr_tables])

        attr_select = shot_table+".shot, " + ','.join(["tmp_%(slug)s.%(slug)s" %{'slug':a.slug} for a in step_attrs])
        query = """CREATE TABLE %(tablename)s SELECT %(attr_select)s FROM %(shot_table)s %(attr_tables)s""" %{'shot_table':shot_table, 'attr_tables':attr_tables, 'tablename':step_tablename, 'attr_select':attr_select}
        cursor.execute(query)
        cursor.execute("CREATE INDEX si on %s(shot)" %step_tablename)

    inner_join_string = ' '.join(["INNER JOIN %(tbl)s ON %(shot_table)s.shot=%(tbl)s.shot" %{"shot_table":shot_table, "tbl":tbl} for tbl in step_tables])

    select_str = shot_table+".shot"
    for step_tablename in step_table_attrs.keys():
        select_str += ', '
        select_str += ', '.join([step_tablename+'.'+i for i in step_table_attrs[step_tablename]])
    try:
        cursor.execute("DROP TABLE %s" %table)
    except:
        pass
    query = "CREATE TABLE %(tablename)s SELECT %(select)s FROM %(shot_table)s %(inner_joins)s" %{"tablename":table, "shot_table":shot_table, "inner_joins":inner_join_string, 'select':select_str}

    cursor.execute(query)
    cursor.execute("CREATE INDEX si on %s(shot)" %table)

    # remove temporary tables
    for tbl in tmp_attr_tables:
        cursor.execute("DROP TABLE %s" %tbl)
    for tbl in step_tables:
        cursor.execute("DROP TABLE %s" %tbl)

def get_last_n(number_of_shots):
    latest_shots = Shot.objects.order_by('-shot')[:number_of_shots]
    return [i.shot for i in latest_shots]


def get_shot_where(shot_q, shot_table='h1ds_summary_shot'):
    shot_ranges = shot_q.split('+')
    individual_shots = []
    group_shots = []
    for shot_range in shot_ranges:
        if shot_range.startswith("last"):
            last_shot = get_last_n(1)[0]
            if shot_range == "last":                
                individual_shots.append(last_shot)
            else:
                group_shots.append([last_shot-int(shot_range[4:])+1,int(last_shot)])
        else:
            limits = shot_range.split('-')
            if len(limits)==1:
                individual_shots.append(int(limits[0]))
            else:
                group_shots.append([int(limits[0]), int(limits[1])])
    shot_filter = " OR ".join("%s.shot BETWEEN %s AND %s" %(shot_table, i[0],i[1]) for i in group_shots)

    if len(individual_shots) > 0:
        if shot_filter != "":
            shot_filter += " OR "
        shot_filter += "%s.shot in (%s)" %(shot_table, ','.join(str(i) for i in individual_shots))
    return shot_filter



class FilterManager(models.Manager):
    def summarydata(self, shot_query="last10", attr_query='default', filter_query=None, table='slave'):
        if table=="slave":
            return self._summarydata_slave(shot_query=shot_query, attr_query=attr_query, filter_query=filter_query)
        else:
            return self._summarydata_master(shot_query=shot_query, attr_query=attr_query, filter_query=filter_query)

    def _summarydata_slave(self, shot_query="last10", attr_query='default', filter_query=None):
        if attr_query=='default':
            attr_list = SummaryAttribute.objects.filter(is_default=True)
        elif attr_query=='all':
            attr_list = SummaryAttribute.objects.all()
        else:
            attr_list = []
            for sl in attr_query.split('+'):
                attr_list.append(SummaryAttribute.objects.get(slug=sl))
        table_name = "summary"
        
        if shot_query.lower() == "all":
            shot_where_clause = ""
        else:
            shot_where_clause = get_shot_where(shot_query, shot_table=table_name)
        attr_select = ', '+', '.join(["%s" %(a.slug) for a in attr_list])

        filter_where = ""

        if filter_query != None:
            filter_strings = filter_query.split("+")
            for fsi,fs in enumerate(filter_strings):
                if not(fsi==0 and shot_where_clause==""):                    
                    filter_where += " AND "
                f = fs.split("__")
                if f[1].lower() == 'gt':
                    filter_where += "%s > %f" %(f[0], float(f[2])) 
                elif f[1].lower() == 'lt':
                    filter_where += "%s < %f" %(f[0], float(f[2])) 
                elif f[1].lower() == 'gte':
                    filter_where += "%s >= %f" %(f[0], float(f[2])) 
                elif f[1].lower() == 'lte':
                    filter_where += "%s <= %f" %(f[0], float(f[2])) 
                elif f[1].lower() in ['bw', 'between']:
                    filter_where += "%s BETWEEN %f AND %f" %(f[0], float(f[2]), float(f[3])) 

        if shot_where_clause == "" and filter_where == "":
            where_str = ""
        else:
            where_str = "WHERE"

        query = """SELECT shot%(attr_select)s FROM %(table_name)s %(where_str)s %(shot_where)s %(filter_where)s ORDER BY shot DESC""" %{'table_name':table_name, 'attr_select':attr_select, 'shot_where':shot_where_clause, 'filter_where':filter_where, 'where_str':where_str}

        cursor = connection.cursor()
        cursor.execute(query)
        return [cursor.fetchall(), attr_list]

    def _summarydata_master(self, shot_query="last10", attr_query='default', filter_query=None):
        if attr_query=='default':
            attr_list = SummaryAttribute.objects.filter(is_default=True)
        elif attr_query=='all':
            attr_list = SummaryAttribute.objects.all()
        else:
            attr_list = []
            for sl in attr_query.split('+'):
                attr_list.append(SummaryAttribute.objects.get(slug=sl))
        
        if shot_query.lower() == "all":
            shot_where_clause = ""
        else:
            shot_where_clause = get_shot_where(shot_query)
        shot_table = 'h1ds_summary_shot'

        attr_select = ', '+', '.join(["att%d.value" %(a.id) for a in attr_list])
        join_list = [i for i in attr_list]

        filter_where = ""

        if filter_query != None:
            filter_strings = filter_query.split("+")
            for fsi,fs in enumerate(filter_strings):
                if not(fsi==0 and shot_where_clause==""):                    
                    filter_where += " AND "
                f = fs.split("__")
                fattr = SummaryAttribute.objects.get(slug=f[0])
                if not fattr in join_list:
                    join_list.append(fattr)
                if f[1].lower() == 'gt':
                    filter_where += "att%d.value > %f" %(fattr.id, float(f[2])) 
                elif f[1].lower() == 'lt':
                    filter_where += "att%d.value < %f" %(fattr.id, float(f[2])) 
                elif f[1].lower() == 'gte':
                    filter_where += "att%d.value >= %f" %(fattr.id, float(f[2])) 
                elif f[1].lower() == 'lte':
                    filter_where += "att%d.value <= %f" %(fattr.id, float(f[2])) 
                elif f[1].lower() in ['bw', 'between']:
                    filter_where += "att%d.value BETWEEN %f AND %f" %(fattr.id, float(f[2]), float(f[3])) 

        attr_tables = ' '.join(["INNER JOIN (SELECT shot_id,value FROM %(this_tbl)s WHERE attribute_id=%(att_id)d) AS att%(att_id)d ON %(shot_tbl)s.shot=att%(att_id)d.shot_id" %{'att_id':a.id,'this_tbl':a.get_att_class()._meta.db_table, 'shot_tbl':shot_table} for a in join_list])
        
        if shot_where_clause == "" and filter_where == "":
            where_str = ""
        else:
            where_str = "WHERE"

        query = """SELECT DISTINCT %(shot_table)s.shot%(attr_select)s FROM %(shot_table)s %(attr_tables)s %(where_str)s %(shot_where)s %(filter_where)s ORDER BY %(shot_table)s.shot DESC""" %{'shot_table':shot_table, 'attr_select':attr_select, 'attr_tables':attr_tables, 'shot_where':shot_where_clause, 'filter_where':filter_where, 'where_str':where_str}

        cursor = connection.cursor()
        cursor.execute(query)
        return [cursor.fetchall(), attr_list]

class FloatAttributeInstance(models.Model):
    shot = models.ForeignKey("Shot")
    attribute = models.ForeignKey("SummaryAttribute")
    value = models.FloatField(null=True, blank=True)

    def sqlrep(self):
        if self.value == None:
            return "NULL"
        else:
            return str(self.value)

    def __unicode__(self):
        return unicode(self.shot) + ' / ' + self.attribute.slug + ' / ' + unicode(self.value)

    def save(self, *args, **kwargs):
        super(FloatAttributeInstance, self).save(*args, **kwargs)
        add_attr_value_to_single_table(self.shot.shot, self.attribute.slug, self.sqlrep())


class IntegerAttributeInstance(models.Model):
    shot = models.ForeignKey("Shot")
    attribute = models.ForeignKey("SummaryAttribute")
    value = models.IntegerField(null=True, blank=True)
    
    def sqlrep(self):
        if self.value == None:
            return "NULL"
        else:
            return str(self.value)

    def __unicode__(self):
        return unicode(self.shot) + ' / ' + self.attribute.slug + ' / ' + unicode(self.value)

    def save(self, *args, **kwargs):
        super(IntegerAttributeInstance, self).save(*args, **kwargs)
        add_attr_value_to_single_table(self.shot.shot, self.attribute.slug, self.sqlrep())
    
    


class DateTimeAttributeInstance(models.Model):
    shot = models.ForeignKey("Shot")
    attribute = models.ForeignKey("SummaryAttribute")
    value = models.DateTimeField(null=True, blank=True)

    def sqlrep(self):
        if self.value == None:
            return "NULL"
        else:
            return "'%s'" %str(self.value)

    def __unicode__(self):
        return unicode(self.shot) + ' / ' + self.attribute.slug + ' / ' + unicode(self.value)


    def save(self, *args, **kwargs):
        super(DateTimeAttributeInstance, self).save(*args, **kwargs)
        add_attr_value_to_single_table(self.shot.shot, self.attribute.slug, self.sqlrep())


datatype_class_mapping = {
    'F':FloatAttributeInstance,
    'I':IntegerAttributeInstance,
    'D':DateTimeAttributeInstance,
    }

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    return '#%02x%02x%02x' % rgb_tuple

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, help_text="Name of the attribute as it appears in the URL")
    name = models.CharField(max_length=500, help_text="Full name of the attribute")
    source = models.CharField(max_length=1000, help_text="Path to script on the filesystem which takes a shot number as a single argument and returns the attribute value")
    short_description = models.TextField()
    full_description = models.TextField()
    data_type = models.CharField(max_length=1, choices=DATATYPE_CHOICES, help_text="Data type used to store attribute in database")
    default_min = models.FloatField(null=True, blank=True, help_text="Optional. Default minimum value used for plots")
    default_max = models.FloatField(null=True, blank=True, help_text="Optional. Default maximum value used for plots")
    display_format = models.CharField(max_length=50,null=True, blank=True, help_text="Optional. Format to display data, e.g.  %%.3f will display 0.1234567 as 0.123.")
    is_default = models.BooleanField(default=False, blank=True, help_text="If true, this attribute will be shown in the default list, e.g. for shot summary.")


    def save(self, *args, **kwargs):
        super(SummaryAttribute, self).save(*args, **kwargs)
        update_attr_single_table(self.slug, datatype_sql[self.data_type])

    def delete(self, *args, **kwargs):
        remove_att_from_single_table(self.slug)
        super(SummaryAttribute, self).delete(*args, **kwargs)
        
        
    def normalise(self, value):
        if value == None or self.default_min == None or self.default_max == None:
            return 0.0
        elif value <= self.default_min:
            return 0.0
        elif value >= self.default_max:
            return 1.0
        else:
            return (value-self.default_min)/(self.default_max-self.default_min)

    def show_barplot(self):
        if self.default_min != None and self.default_max != None:
            return True
        else:
            return False

    def colourise(self, value):
        norm = (-2.0/3*self.normalise(value)) + 2.0/3
        rgb =  tuple([int(255.0*i) for i in hsv_to_rgb(norm, 0.6, 0.95)])
        return RGBToHTMLColor(rgb)

    def __unicode__(self):
        return self.name

    def get_att_class(self):
        return datatype_class_mapping[self.data_type]

    def get_datatype(self):
        return datatype_python[self.data_type]

    def get_instances(self):
        return self.get_att_class().objects.filter(attribute=self)
    
    def delete_instances(self):
        self.get_instances().delete()

    def get_value(self, shot_number):
        # we write to a temp file in the filesystem rather than give webserver privs to pipe
        tmpname = '/tmp/'+uuid.uuid4().hex
        sub = subprocess.call(self.source+' '+str(shot_number)+' > %s' %tmpname, shell=True)
        f = open(tmpname)
        data = f.read()
        f.close()
        sub = subprocess.call('/bin/rm %s' %tmpname, shell=True)        
        try:
            if data.strip().lower() in ['null', 'none']:
                return None
            else:
                return datatype_python[self.data_type](data)
        except ValueError:
            return None

    def _get_value(self, shot_number):
        # we write to a temp file in the filesystem rather than give webserver privs to pipe
        tmpname = '/tmp/'+uuid.uuid4().hex
        sub = subprocess.call('/home/datasys/code/test/dummy_data.py'+' '+str(shot_number)+' > %s' %tmpname, shell=True)
        f = open(tmpname)
        data = f.read()
        f.close()
        sub = subprocess.call('/bin/rm %s' %tmpname, shell=True)        
        if data.strip().lower() in ['null', 'none']:
            return None
        else:
            return datatype_python[self.data_type](data)


class Shot(models.Model):
    shot = models.IntegerField(primary_key=True)

    objects = FilterManager()

    def __unicode__(self):
        return unicode(self.shot)

    def delete(self):
        delete_shot_from_single_table(self.shot)
        super(Shot, self).delete()

from h1ds_summary.tasks import generate_shot


def new_shot_callback(sender, **kwargs):
    """generate new shot when new_shot_signal is received."""
    result = generate_shot.delay(kwargs['shot'])

## TODO: hook up to h1ds_signal - where to specify h1ds_signal name? should we have a dedicated new shot signal?
#new_shot_signal.connect(new_shot_callback)

