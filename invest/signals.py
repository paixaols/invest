from django.db.models.signals import post_save

from .models import Asset, Content, GroupAgg, MarketAgg
from .utils import qs_to_df


def aggregate_wallet_contents(sender, instance, created, **kwargs):
    wallet_id = instance.wallet_id
    user_id = instance.user_id

    # Conteúdo da carteira
    df_content = qs_to_df(
        Content.objects.filter(wallet_id=wallet_id)
    )

    # Associar info dos ativos
    asset_ids = df_content['asset_id'].unique()
    df_assets = qs_to_df(
        Asset.objects.filter(pk__in=asset_ids)
    )
    df_content = df_content.merge(
        df_assets, how='left', left_on='asset_id', right_on='id',
        suffixes=('', '_asset')
    )

    # Agregar valores
    market_agg = df_content[['market_id', 'cost', 'value']].groupby('market_id').sum().reset_index()
    group_agg = df_content[['market_id', 'group_id', 'cost', 'value']].groupby(['market_id', 'group_id']).sum().reset_index()

    # Inserir ou atualizar BD
    market_agg['defaults'] = market_agg.apply(lambda x: x.to_dict(), axis=1)
    market_agg['update_create'] = market_agg.apply(
        lambda x: MarketAgg.objects.update_or_create(
            user_id=user_id,
            wallet_id=wallet_id,
            market_id=x['market_id'],
            defaults=x['defaults']
        ),
        axis=1
    )

    group_agg['defaults'] = group_agg.apply(lambda x: x.to_dict(), axis=1)
    group_agg['update_create'] = group_agg.apply(
        lambda x: GroupAgg.objects.update_or_create(
            user_id=user_id,
            wallet_id=wallet_id,
            market_id=x['market_id'],
            group_id=x['group_id'],
            defaults=x['defaults']
        ),
        axis=1
    )

    # Remover agregações não mais existentes
    current_market_ids = market_agg['market_id'].to_list()
    qs = MarketAgg.objects.filter(wallet_id=wallet_id)
    drop_agg_ids = [ agg.id for agg in qs if agg.market_id not in current_market_ids ]
    if len(drop_agg_ids) > 0:
        MarketAgg.objects.filter(pk__in=drop_agg_ids).delete()

    current_aggs = zip(
        group_agg['market_id'].to_list(),
        group_agg['group_id'].to_list()
    )
    current_aggs = list(current_aggs)
    qs = GroupAgg.objects.filter(wallet_id=wallet_id)
    drop_agg_ids = [ agg.id for agg in qs if (agg.market_id, agg.group_id) not in current_aggs ]
    if len(drop_agg_ids) > 0:
        GroupAgg.objects.filter(pk__in=drop_agg_ids).delete()


post_save.connect(aggregate_wallet_contents, sender=Content)
