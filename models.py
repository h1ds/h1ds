import subprocess, shlex, uuid
from django.db import models, connection
from colorsys import hsv_to_rgb

from h1ds_interface.signals import new_shot_signal

DATATYPE_CHOICES = (
    ('F', 'Float'),
    ('I', 'Integer'),
    ('D', 'Date and time'),
    ('T', 'Text'),
    )

datatype_python = {
    'F':float,
    }

def get_last_n(number_of_shots):
    latest_shots = Shot.objects.order_by('-shot')[:number_of_shots]
    return [i.shot for i in latest_shots]


def get_shot_where(shot_q):
    shot_table = 'h1ds_summary_shot'
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
    def summarydata(self, shot_query="last10", attr_query='all', filter_query=None):
        if attr_query=='all':
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

    def __unicode__(self):
        return unicode(self.shot) + ' / ' + self.attribute.slug + ' / ' + unicode(self.value)

datatype_class_mapping = {
    'F':FloatAttributeInstance,
    }

def RGBToHTMLColor(rgb_tuple):
    """ convert an (R, G, B) tuple to #RRGGBB """
    return '#%02x%02x%02x' % rgb_tuple

class SummaryAttribute(models.Model):
    slug = models.SlugField(max_length=100, help_text="Name of the attribute as it appears in the URL")
    name = models.CharField(max_length=500, help_text="Full name of the attribute")
    source = models.CharField(max_length=1000, help_text="Path to script on the filesystem which takes a shot number as a single argument and returns the attribute value")
    description = models.TextField()
    data_type = models.CharField(max_length=1, choices=DATATYPE_CHOICES, help_text="Data type used to store attribute in database")
    default_min = models.FloatField(null=True, blank=True, help_text="Optional. Default minimum value used for plots")
    default_max = models.FloatField(null=True, blank=True, help_text="Optional. Default maximum value used for plots")
    display_format = models.CharField(max_length=50,null=True, blank=True, help_text="Optional. Format to display data, e.g.  %%.3f will display 0.1234567 as 0.123.")


    def normalise(self, value):
        if value <= self.default_min:
            return 0.0
        elif value >= self.default_max:
            return 1.0
        else:
            return (value-self.default_min)/(self.default_max-self.default_min)

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
        if data.strip().lower() in ['null', 'none']:
            return None
        else:
            return datatype_python[self.data_type](data)

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


from h1ds_summary.tasks import generate_shot

def new_shot_callback(sender, **kwargs):
    """generate new shot when new_shot_signal is received."""
    result = generate_shot.delay(kwargs['shot'])

new_shot_signal.connect(new_shot_callback)
