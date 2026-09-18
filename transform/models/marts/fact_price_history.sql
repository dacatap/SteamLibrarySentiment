with source as (
    select * from {{ref('stg_itad_pricehistory')}}
)

select
    steam_app_id,
    price_timestamp,
    price_date,
    price_amount,
    regular_price,
    discount_pct
from source