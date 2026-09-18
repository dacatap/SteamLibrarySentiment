with source as (
    select * from {{ref('stg_steam_reviews')}}
),

deduped as (
    select *,
        row_number() over (
            partition by steam_app_id, review_date
            order by case when data_grain = 'daily' then 1 else 2 end
        ) as rn
    from source
)

select
    steam_app_id,
    review_date,
    recommendations_up,
    recommendations_down,
    data_grain
from deduped
where rn = 1