with source as (
    select * from {{ref('stg_steamcharts_players')}}
)

select
    steam_app_id,
    recorded_date,
    avg_players
from source