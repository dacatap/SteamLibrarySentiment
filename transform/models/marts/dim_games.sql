with source as (
    select * from {{ref('stg_itad_gameinfo')}}
)
select
    steam_app_id,
    itad_id,
    title,
    release_date,
    early_access,
    tags,
    developers,
    publishers
from source