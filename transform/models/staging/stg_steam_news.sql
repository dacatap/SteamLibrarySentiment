with source as (
    select *
    from read_parquet('s3://amzn-s3-steam-itad-charts-data-209186716412-sa-east-1-an/raw/Steam/news/*/*.parquet')
),

unnested as (
    select
        steam_game_id::varchar                              as steam_app_id,
        unnest(appnews.newsitems)                           as item
    from source
),

final as (
    select
        steam_app_id,
        item.gid::varchar                                   as gid,
        item.title::varchar                                 as title,
        epoch_ms(item.date::bigint * 1000)::date            as published_date,
        item.url::varchar                                   as url,
        item.contents::varchar                              as contents_preview
    from unnested
)

select * from final