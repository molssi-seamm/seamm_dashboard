import datetime
from flask_login import current_user
from .. import db


"""
Fields: http://docs.mongoengine.org/apireference.html
mongoengine.fields.

Field Options:
-------------
    db_field: Specify a different field name
    required: Make sure this field is set
    default: Use the given default value if no other value is given
    unique: Make sure no other document in the collection has the same value for this field
    choices: Make sure the field's value is equal to one of the values given in an array
"""


class QMFeatures(db.EmbeddedDocument):
    """QM specific features"""

    basis = db.StringField(max_length=200)
    element_coverage = db.StringField(max_length=200)
    other = db.StringField(max_length=250)

    # tags
    TAG_NAMES = [
                "semiempirical",  # fff
                "dft",
                "dft_u",
                "hybrid",
                "rohf",
                "uhf",
                "mcscf",
                "ci",
                "mp_or_mbpt",
                "cc",
                "rpa",
                "gf",
                "tddft",
                "dmf",
                "frequencies_phonons",
                "nmr",
                "symmetry"
    ]

    tags = db.ListField(db.StringField(max_length=20, choices=TAG_NAMES))

    def add_tags(self, kwargs):
        self.tags = []
        for tag in self.TAG_NAMES:
            if tag in kwargs:
                tag_val = kwargs.pop(tag, '')
                if tag_val and tag_val.lower() not in ['', 'no', 'false']:
                    self.tags.append(tag)

    def is_empty(self):
        if self.basis or self.element_coverage or self.other or self.tags:
            return False
        else:
            return True


class MMFeatures(db.EmbeddedDocument):
    """MM specific features"""

    ENSEMBLES = ['DPD', 'Langevin Dynamics', 'NPH', 'NPT', 'NVE', 'NVT', 'NgammaP', 'NgammaT']
    FORCEFIELD_TYPES = ["Class I", "Class II", "Polarizable", "Reactive", "Inorganic/Metals"]

    ensembles = db.ListField(db.StringField(max_length=20, choices=ENSEMBLES))
    free_energy_methods = db.StringField(max_length=200)
    advanced_sampling_methods = db.StringField(max_length=200)

    forcefields = db.StringField(max_length=200, help_text='')
    forcefield_types = db.ListField(db.StringField(max_length=20, choices=FORCEFIELD_TYPES))
    file_formats = db.StringField(max_length=200, help_text='What are the supported input file formats?')
    qm_mm = db.BooleanField(verbose_name='QM/MM')

    # tags
    TAG_NAMES = [
                "periodicity_0d",
                "periodicity_1_and_2d",
                "periodicity_3d",
                "constraints",
                "rigid_bodies",
                "restraints",
                "monte_carlo",
                "rnemd",     # RNMED
                "analysis_tools",
                "building_tools",
                "implicit_solvent",

    ]

    tags = db.ListField(db.StringField(max_length=20, choices=TAG_NAMES))

    def add_tags(self, kwargs):
        self.tags = []
        for tag in self.TAG_NAMES:
            if tag in kwargs:
                tag_val = kwargs.pop(tag, '')
                if tag_val and tag_val.lower() not in ['', 'no', 'false']:
                    self.tags.append(tag)

    def is_empty(self):
        if self.ensembles or self.free_energy_methods or self.advanced_sampling_methods \
                or self.forcefields or self.forcefield_types or self.file_formats \
                or self.qm_mm or self.tags:
            return False
        else:
            return True


class Software(db.DynamicDocument):     # flexible schema, can have extra attributes

    # added by
    added_by_name = db.StringField(max_length=150, required=True)
    added_by_email = db.EmailField(required=True)
    is_SW_owner = db.BooleanField(default=False)

    # availability
    software_name = db.StringField(max_length=150, required=True)
    license = db.StringField(max_length=200, required=True, help_text='E.g., GPL, BSD-3, proprietary, ...')
    price = db.StringField(max_length=200, help_text='E.g., free, free for academia, $600 for one year, ...')
    latest_version = db.StringField(max_length=100)
    date_of_latest_version = db.DateTimeField()            # Date of latest version
    principal_contact_name = db.StringField(max_length=150)
    principal_contact_email = db.EmailField()
    official_website = db.URLField(required=True, help_text='E.g., http://www.molssi.org')

    # Others
    description = db.StringField(required=True, default='',
                                 help_text='Short description of max 500 characters')
    long_description = db.StringField(required=True, default='', help_text='Longer detailed description')
    comments = db.StringField()
    required_citation = db.StringField(help_text='Which papers need to be cited when this software is used')
    domain = db.StringField(required=True, default='MM', choices=['MM', 'QM', 'other'])

    # software engineering
    LANGUAGES = ['C', 'C++', 'Python', 'FORTRAN', 'FORTRAN2003', 'FORTRAN77',
                 'FORTRAN90', 'Java', 'JavaScript', 'Other']

    source_code_link = db.URLField()
    executables = db.StringField(max_length=150,
                    help_text='Are pre-compiled distributions available? which operating systems are supported?')
    code_management = db.StringField(max_length=10,
                                choices=['', 'git/GitHub', 'git/Bitbucket', 'git/others', 'SVN', 'CVS', 'other'])
    continuous_integration = db.StringField(max_length=20, choices=['', 'Yes', 'No'])
    number_of_tests = db.IntField()
    languages = db.ListField(db.StringField(max_length=20, choices=LANGUAGES), required=True)
    # for search efficiency, repeat in lowercase, keep original case for display
    languages_lower = db.ListField(db.StringField(max_length=20))
    compilers = db.StringField(max_length=100)

    # Performance
    parallel = db.StringField(max_length=50, choices=['', 'Yes', 'No'])
    gpu = db.StringField(max_length=50, choices=['', 'Yes', 'No'], verbose_name='GPU')
    knl_optimized = db.StringField(max_length=50, choices=['', 'Yes', 'No'], verbose_name='KNL Optimized')

    # support
    support_line = db.StringField(max_length=250, help_text='URL or email')  # url or email
    documentation = db.URLField()
    number_of_tutorials = db.IntField()
    wiki = db.URLField()
    forum = db.URLField()
    mail_list = db.URLField()
    gui = db.BooleanField(verbose_name='GUI')

    # Local
    # published = DateTimeField()b
    date_added = db.DateTimeField(default=datetime.datetime.now)
    last_updated = db.DateTimeField()
    last_updated_by = db.StringField()
    is_pending = db.BooleanField(default=True, help_text='If checked, the software will not be public')

    mm_features = db.EmbeddedDocumentField(MMFeatures, verbose_name='MM Features')

    qm_features = db.EmbeddedDocumentField(QMFeatures, verbose_name='QM Features')

    # Use the $ prefix to set a text index
    meta = {
        # 'allow_inheritance': True,  # known issue with text search
        'strict': False,    # allow extra fields
        'indexes': [
            "domain",
            {
                'fields': ['$software_name', "$description", "$long_description"],
                'default_language': "en",
                "language_override": "en",
            }
        ]
    }

    def __unicode__(self):
        return self.software_name

    @property
    def software_type(self):
        return self.__class__.__name__

    def save(self, *args, **kwargs):
        """Override save to add languages_lower"""
        self.add_language_lower()
        self.last_updated = datetime.datetime.now
        self.last_updated_by = str(current_user)

        if self.mm_features and self.mm_features.is_empty():
            self.mm_features = None

        if self.qm_features and self.qm_features.is_empty():
            self.qm_features = None

        return super(Software, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.id) + ', name: ' + self.software_name + ', is_pending: ' + \
                str(self.is_pending) + ', Domain: ' + self.domain

    def add_language_lower(self):
        if self.languages:
            self.languages_lower = [lang.lower() for lang in self.languages]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def props(cls):
    all_props = [i for i in cls.__dict__.keys() if i[:1] != '_']
    all_props.remove('tags')
    all_props.remove('TAG_NAMES')
    all_props.remove('add_tags')
    return all_props


def set_props_values(cls, obj, prop_values):
    for prop in props(cls):
            if prop in prop_values:
                tag_val = prop_values.pop(prop, '')
                if tag_val:  # and tag_val.lower() not in ['', 'no', 'false']:
                    setattr(obj, prop, tag_val)


def create_software(lib_type='', **kwargs):
    """Create a Library object from a set of params
       A Builder Design Pattern"""

    if lib_type == 'MM':
        mm_features = MMFeatures()
        set_props_values(MMFeatures, mm_features, kwargs)
        mm_features.add_tags(kwargs)
        lib = Software(mm_features=mm_features, **kwargs)

    elif lib_type == 'QM':
        qm_features = QMFeatures()
        set_props_values(QMFeatures, qm_features, kwargs)
        qm_features.add_tags(kwargs)
        lib = Software(qm_features=qm_features, **kwargs)

    else:
        lib = Software(**kwargs)

    return lib
