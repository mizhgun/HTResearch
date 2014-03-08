import mongoengine as mongo


class UrlCountPairDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for pairing Source URLs and the Number of References to some Page"""

    url = mongo.URLField(db_field='u')
    count = mongo.LongField(min_value=0, db_field='c')


class PageRankVectorDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for counting referenced organizations"""

    org_domain = mongo.StringField(db_field='o')
    count = mongo.LongField(min_value=0, db_field='c')
    pages = mongo.ListField(field=mongo.EmbeddedDocumentField(document_type=UrlCountPairDTO), db_field='p')


class PageRankInfoDTO(mongo.EmbeddedDocument):
    """A DTO wrapper for Information related to PageRank """

    total_with_self = mongo.LongField(min_value=0, db_field='ts')
    total = mongo.LongField(min_value=0, db_field='t')
    references = mongo.ListField(field=mongo.EmbeddedDocumentField(document_type=PageRankVectorDTO), db_field='r')