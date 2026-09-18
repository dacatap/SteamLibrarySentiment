with source as (
    select * from {{ref('stg_steam_news')}}
)

select
    steam_app_id,
    gid,
    title,
    published_date,
    url,
    contents_preview
from source