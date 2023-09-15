#!/usr/bin/env python
"""category.py: Declaratively mapped Categories from IncidentIQ

Category contains the methods nescessary to pull and transofrm
the data from the IncidentIQ to conform to declaratively mapped
object in SqlAlcemy. Category can be instantiated with data from
IncidentIQ to insert into the specified database.
"""

from requests.models import HTTPError
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
    CategoryId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)
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
    # DbId = Column(UNIQUEIDENTIFIER(binary=False), primary_key=True)

    # List of fields allows insertion via setattr() easily, as well as
    # validation without needless code
    fields = [
        'AppId', 'CategoryId', 'CategoryTypeId', 'CategoryTypeName', 'Description',
        'Icon', 'Level', 'Name', 'NameWithParent', 'ParentCategoryId',
        'ParentCategoryName', 'Scope', 'SiteId', 'SortOrder' # , 'DbId'
    ]

    @validates(*fields)
    def validate_inserts(self, key, value):
        return super().validate_inserts(key, value)

    def __init__(self, data):
        # Extract fields from the raw data, optional fields are retrieved
        # safely via find_element
        for field in self.fields:
            # For non-nested fields that exist at the first level of the JSON
            # we can use setattr to assign values, since the fields are
            # named exactly as they appear in the JSON. Convention over configuration
            # wins here. For example, an asset JSON response will have a field 'AssetId'
            # at the base level of that item. Thus, find_element can grab it simply by being
            # passed 'AssetId'. By design, the column is also named 'AssetId', so we can
            # iterate simply and set these fields.
            setattr(self, field, IIQ.find_element(data, field))

        # Nested fields are more complex, and thus are commented in the declaration
        # as Nested. We simply path these out by hand since there are only a few, and
        # often they are purposeful inclusions that aren't nescessary but useful to
        # end users. This is harmless even if they are optional fields in the API response,
        # since find_element will set them to None by default
        # self.DbId = uuid4()

    @staticmethod
    def get_data_request(page):
        # url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/categories?$p=" + str(
        #     page) + "&$s=" + config.PAGE_SIZE + "&$d=Ascending&$o=NameWithParent"
        url = url = "https://" + config.IIQ_INSTANCE + "/api/v1.0/categories?$p=" + str(page)  + "&$s=" + config.PAGE_SIZE

        # payload = "{ \"Strategy\" : \"FullHierarchy\" }"
        payload = "{ \"AcrossAllProducts\" : \"True\",\n \"Strategy\": \"FullHierarchy\" }"
        headers = {
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
            'Client': 'WebBrowser',
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/plain, */*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Authorization': 'Bearer ' + config.IIQ_TOKEN
        }

        response = requests.request("POST",
                                    url,
                                    headers=headers,
                                    data=payload,
                                    timeout=config.TIMEOUT)
        # Cause an exception if anything but success is returned
        if response.status_code != 200:
            print("ERROR: STATUS CODE NOT 200")
            raise HTTPError("""A request returned a status code other than 200\n
            Status Code: """ + str(response.status_code))

        # Cause an exception if for some reason the API returns nothing
        if response.json()['Paging']['PageSize'] <= 0:
            print("ERROR NO ELEMENTS WERE RETURNED")
            raise HTTPError("No elements were returned from a request")

        return response

    @staticmethod
    def get_num_pages():
        return Category.get_data_request(0).json()['Paging']['PageCount']

    @classmethod
    def get_page(cls, page_number):
        return super().get_page(page_number)
