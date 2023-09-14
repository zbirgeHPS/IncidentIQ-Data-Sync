# A category class representing IncidentIQ Locaitons
from sqlalchemy import Column, String, Integer, Date, Boolean, Numeric
from sqlalchemy_utils.types.uuid import UUIDType as UNIQUEIDENTIFIER
from sqlalchemy.orm import validates
from base import Base, IIQ_Datatype as IIQ
from uuid import uuid4
import config
import requests


class Category(Base, IIQ):
    """Category is an instanciable class which holds all the information
    for one Category in IncidentIQ. Category also contains methods to make an
    API request to retreive an entire page of Categorys. Category is declaratively 
    mapped in SqlAlchemy to the 'Categorys' table.
    (by default, differs by configurable table names).
    On instantiation Category can be inserted into 'Categorys' via an SqlAlchemy
    session."""
    __tablename__ = config.CATEGORIES_TABLE_NAME
    if config.SCHEMA is not None:
        __table_args__ = {'schema': config.SCHEMA}

    AppId = Column(String(length=config.STRING_LENGTH))
    CategoryId = Column(UNIQUEIDENTIFIER(binary=False))
    CategoryTypeId = Column(UNIQUEIDENTIFIER(binary=False))
    CategoryTypeName = Column(String(length=config.STRING_LENGTH))
    Description = Column(String(length=config.STRING_LENGTH))
    Icon = Column(String(length=config.STRING_LENGTH))
    Level = Column(Integer)
    Name = Column(String(length=config.STRING_LENGTH))
    NameWithParent = Column(String(length=config.STRING_LENGTH))
    ParentCategoryId =  Column(UNIQUEIDENTIFIER(binary=False))
    ParentCategoryName = Column(String(length=config.STRING_LENGTH))
    Scope = Column(String(length=config.STRING_LENGTH))
    SiteId =  Column(UNIQUEIDENTIFIER(binary=False))
    SortOrder = Column(Integer)
    DbId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)

    fields = [
        'AppId', 'CategoryId', 'CategoryTypeId', 'CategoryTypeName', 'Description',
        'Icon', 'Level', 'Name', 'NameWithParent', 'ParentCategoryId',
        'ParentCategoryName', 'Scope', 'SiteId', 'SortOrder', 'DbId'
    ]

    @validates(*fields)
    def validate_inserts(self, key, value):
        return super().validate_inserts(key, value)

    def __init__(self, data):
        # Extract fields from the raw data, optional nested fields
        # can be retrieved easily with find_element *args (See asset.py)
        for field in self.fields:
        # For non-nested fields that exist at the first level of the JSON
        # we can use setattr to assign values, since the fields are
        # named exactly as they appear in the JSON. For example, an asset
        # JSON response will have a field 'AssetId' at the base level of that item.
        # Thus, find_element can grab it simply by being passed 'AssetId'. By design,
        # the column is also named 'AssetId', so we can iterate simply and set these fields.
            setattr(self, field, IIQ.find_element(data, field))

        # Nested fields are more complex, and thus are commented in the declaration
        # as Nested. We simply path these out by hand since there are only a few, and
        # often they are purposeful inclusions that aren't nescessary but useful to
        # end users. This is harmless even if they are optional fields in the API response,
        # since find_element will set them to None by default

        self.DbId = uuid4()

    @staticmethod
    def get_data_request(page_number):
        url = "https://" + config.IIQ_INSTANCE + "/api/V1.0/categories?$p=" + str(
            page_number) + "&$s=" + str(config.PAGE_SIZE)

        payload = {}
        headers = {
            'Connection': 'keep-alive',
            'Client': 'WebBrowser',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        return requests.request("POST",
                                url,
                                headers=headers,
                                data=payload,
                                timeout=config.TIMEOUT)

    @staticmethod
    def get_num_pages():
        return Category.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
