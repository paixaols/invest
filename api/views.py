from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import (
    AssetSerializer, AssetGroupSerializer, AssetTypeSerializer, MarketSerializer
)
from invest.models import Asset, AssetGroup, AssetType, Market


@api_view(['GET'])
def get_assets(request):
    data = request.GET
    data = { k: int(v) for k, v in data.items() }
    if data:
        assets = Asset.objects.filter(**data).order_by('name')
    else:
        assets = Asset.objects.all().order_by('name')
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_asset_groups(request):
    groups = AssetGroup.objects.all().order_by('group')
    serializer = AssetGroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_asset_types(request):
    types = AssetType.objects.all().order_by('type')
    serializer = AssetTypeSerializer(types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_markets(request):
    markets = Market.objects.all().order_by('name')
    serializer = MarketSerializer(markets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
