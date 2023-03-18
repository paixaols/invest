from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import (
    AssetSerializer, AssetGroupSerializer, AssetTypeSerializer, MarketSerializer
)
from invest.models import Asset, AssetGroup, AssetType, Market


@api_view(['GET'])
def get_assets(request):
    assets = Asset.objects.all()
    serializer = AssetSerializer(assets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_asset_groups(request):
    groups = AssetGroup.objects.all()
    serializer = AssetGroupSerializer(groups, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_asset_types(request):
    types = AssetType.objects.all()
    serializer = AssetTypeSerializer(types, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_markets(request):
    markets = Market.objects.all()
    serializer = MarketSerializer(markets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
