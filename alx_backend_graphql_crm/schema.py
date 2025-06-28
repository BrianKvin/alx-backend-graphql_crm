import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


class Query(CRMQuery, graphene.ObjectType):
    """Main GraphQL Query class combining all app queries"""
    pass


class Mutation(CRMMutation, graphene.ObjectType):
    """Main GraphQL Mutation class combining all app mutations"""
    pass


# Main schema object
schema = graphene.Schema(query=Query, mutation=Mutation)