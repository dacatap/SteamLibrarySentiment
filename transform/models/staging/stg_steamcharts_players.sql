with source as (
    select *
    from read_parquet('s3://amzn-s3-steam-itad-charts-data-209186716412-sa-east-1-an/raw/SteamCharts/playercounts/*/*.parquet')
),

final as (
    select
        steam_game_id::varchar as steam_app_id,
        epoch_ms(timestamp)::date as recorded_date,
        avg_players::int as avg_players
    from source
)

select * from final