with source as (
    select *
    from read_parquet('s3://amzn-s3-steam-itad-charts-data-209186716412-sa-east-1-an/raw/ITAD/gameinfo/*.parquet')
),

renamed as (
    select
        steam_app_id::varchar       as steam_app_id,
        itad_id::varchar            as itad_id,
        title::varchar              as title,
        releaseDate::date           as release_date,
        earlyAccess::boolean        as early_access,
        tags,
        developers,
        publishers
    
    from source
)

select * from renamed