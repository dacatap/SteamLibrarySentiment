with source as (
    select *
    from read_parquet('s3://amzn-s3-steam-itad-charts-data-209186716412-sa-east-1-an/raw/ITAD/pricehistory/*/*.parquet')
),

final as (
    select
        steam_game_id::varchar          as steam_app_id,
        timestamp::timestamp            as price_timestamp,
        timestamp::date                 as price_date,
        price_amount::float             as price_amount,
        regular_price::float            as regular_price,
        discount_pct::int               as discount_pct
    from source
)

select * from final