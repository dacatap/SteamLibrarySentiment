with source as (
    select *
    from read_parquet('s3://amzn-s3-steam-itad-charts-data-209186716412-sa-east-1-an/raw/Steam/reviews/*/*.parquet')
),

rollups as (
    select
        steam_game_id::varchar                              as steam_app_id,
        unnest(results.rollups)                             as review,
        'monthly'                                           as data_grain
    from source
),

recent as (
    select
        steam_game_id::varchar                              as steam_app_id,
        unnest(results.recent)                              as review,
        'daily'                                             as data_grain
    from source
),

combined as (
    select * from rollups
    union all
    select * from recent
),

final as (
    select
        steam_app_id::varchar                           as steam_app_id,
        epoch_ms(review.date::bigint * 1000)::date      as review_date,
        review.recommendations_up::int                  as recommendations_up,
        review.recommendations_down::int                as recommendations_down,
        data_grain
    from combined
)

select * from final