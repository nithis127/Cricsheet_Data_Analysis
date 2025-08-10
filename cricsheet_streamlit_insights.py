import streamlit as st
import pymysql
import pandas as pd

#---function for connect Python to MySQL database---
def get_connection():
    return pymysql.connect(host='localhost',
                      user='root',
                      password='12345',
                      database='cricsheet',
                      port=3306,
                      cursorclass=pymysql.cursors.DictCursor
                      )

#---function for run SQL query---
def run_query(query):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:                    #automatically closes the connection after block execution
        with cursor:                    #automatically closes the cursor after block execution
            cursor.execute(query)
            result = cursor.fetchall()
    return pd.DataFrame(result)         #return converts fetch result to pandas dataframe

def set_background(image_url):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("{image_url}");
            background-attachment: fixed;
            background-size: cover;
            background-position: center;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("https://t3.ftcdn.net/jpg/07/88/73/76/360_F_788737654_KYGxDOeiVinLr0lpTL0xBDqGNxZiyUFV.jpg")

st.header('🏏 Cricket Insights Dashboard')     #streamlit dashboard header

#---creates collapsible sections with specific insights---
with st.expander("**01. 🏏 Top 10 Batsmen by Total Runs with Team (International Matches)**"):
    query = '''
                select batter, team, sum(total_runs) as total_runs
                from (
                    select batter, team, sum(batter_runs) as total_runs from odi_deliveries group by batter, team
                    union all
                    select batter, team, sum(batter_runs) as total_runs from t20_deliveries group by batter, team
                    union all
                    select batter, team, sum(batter_runs) as total_runs from test_deliveries group by batter, team
                    ) as all_player_runs
                group by batter, team order by total_runs desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**02. 🎯 Top 10 Leading Wicket-Takers in International Matches**"):
    query = '''
                select bowler, count(*) as taken_wickets
                from (
                    select bowler from odi_deliveries
                    where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                        ((wicket is not null) or
                        (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler or fielder_4 = bowler))
                    union all 
                    select bowler from t20_deliveries
                    where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                        ((wicket is not null) or
                        (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                    union all 
                    select bowler from test_deliveries
                    where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                        ((wicket is not null) or
                        (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                    ) as all_wic_takers
                group by bowler
                order by taken_wickets desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**03. 🏆 Team with the Highest Win Percentage in Test Cricket**"):
    query = '''
                select match_winner, 
                    round((count(*) * 100/(select count(*) 
                            from test_matches 
                            where match_winner is not null)
                            ),2) as winning_percentage
                from test_matches where match_winner is not null
                group by match_winner
                order by winning_percentage desc limit 1;
            '''
    st.write(run_query(query))

with st.expander("**04. 💯 Total Number of Centuries Across All Match Types**"):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        with cursor:
            queries = [
                        '''
                            create temporary table if not exists  ipl_centuries as
                                select match_id, team, floor(sum(batter_runs)/100) as centuries
                                from ipl_deliveries
                                group by match_id, team having sum(batter_runs)>=100;
                            ''',
                            '''    
                            create temporary table if not exists  odi_centuries as
                                select match_id, team, floor(sum(batter_runs)/100) as centuries
                                from odi_deliveries 
                                group by match_id, team having sum(batter_runs)>=100;
                            ''',
                            '''    
                            create temporary table if not exists  t20_centuries as
                                select match_id, team, floor(sum(batter_runs)/100) as centuries
                                from t20_deliveries
                                group by match_id, team having sum(batter_runs)>=100;
                            ''',
                            '''    
                            create temporary table if not exists  test_centuries as
                                select match_id, team, floor(sum(batter_runs)/100) as centuries
                                from test_deliveries 
                                group by match_id, team having sum(batter_runs)>=100;
                            ''']
            # Run each query one by one
            for q in queries:
                cursor.execute(q) 
            # Final query to get the total centuries
            final_query = '''
                            select 
                                ipl.ipl,
                                odi.odi,
                                t20.t20,
                                test.test,
                                (ipl.ipl + odi.odi + t20.t20 + test.test) as total_centuries
                            from
                                (select sum(centuries) as ipl from ipl_centuries) as ipl
                            cross join 
                                (select sum(centuries) as odi from odi_centuries) as odi
                            cross join
                                (select sum(centuries) as t20 from t20_centuries) as t20
                            cross join
                                (select sum(centuries) as test from test_centuries) as test;
                        '''
            cursor.execute(final_query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            st.write(df)

with st.expander("**05. 🔥 Matches with the Narrowest Margin of Victory**"):
    query = '''
                select * 
                    from ( 
                        (select season, match_name, teams, match_winner
                        from ipl_matches where (win_by_wickets<2) or (win_by_runs<2))
                        union all
                        (select season, match_name, teams, match_winner
                        from odi_matches where (win_by_wickets<2) or (win_by_runs<2))
                        union all
                        (select season, match_name, teams, match_winner
                        from t20_matches where (win_by_wickets<2) or (win_by_runs<2))
                        union all 
                        (select season, match_name, teams, match_winner
                        from test_matches where (win_by_wickets<2) or (win_by_runs<2) or (win_by_innings<2))
                        ) as narrow_vitories 
                order by season, match_name;
            '''
    st.write(run_query(query))

with st.expander("**06. 🎳 Players with 100+ Wickets in All Three International Match Types**"):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        with cursor:
            queries = ['''
                        create temporary table if not exists odi_wic
                            select  bowler, count(wicket) as wickets from odi_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler or fielder_4 = bowler))
                            group by  bowler having count(wicket)>=100;
                        ''',
                        '''
                        create temporary table if not exists t20_wic
                            select  bowler, count(wicket) as wickets from t20_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                            group by  bowler having count(wicket)>=100;
                        ''',
                        '''
                        create temporary table if not exists test_wic
                            select  bowler, count(wicket) as wickets from test_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                            group by  bowler having count(wicket)>=100;
                        ''']
            for q in queries:
                cursor.execute(q)
            final_query = '''
                            SELECT o.bowler, o.wickets AS odi_wickets, t.wickets AS t20_wickets, ts.wickets AS test_wickets
                            FROM odi_wic o
                            JOIN t20_wic t ON o.bowler = t.bowler
                            JOIN test_wic ts ON o.bowler = ts.bowler;
                        '''
            cursor.execute(final_query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            st.write(df)

with st.expander("**07. 🥇 Top 5 Players with Most Man-of-the-Match Awards**"):
    query = '''
                select player_of_match as man_of_the_match, sum(total_matches) as total_matches
                from (
                    (select player_of_match, count(*) as total_matches from ipl_matches
                    where player_of_match is not null
                    group by player_of_match)
                    union all
                    (select player_of_match, count(*) as total_matches from odi_matches
                    where player_of_match is not null
                    group by player_of_match)
                    union all
                    (select player_of_match, count(*) as total_matches from t20_matches
                    where player_of_match is not null
                    group by player_of_match)
                    union all
                    (select player_of_match, count(*) as total_matches from test_matches
                    where player_of_match is not null
                    group by player_of_match)
                    ) as all_matches
                group by player_of_match having player_of_match is not null
                order by sum(total_matches) desc limit 5;
            '''
    st.write(run_query(query))

with st.expander("**08. 🧢 Players with 10,000+ International Runs & 100+ IPL Matches**"):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        with cursor:
            query = '''
                        create temporary table if not exists inter_matches
                            select batter as player, sum(total_runs) as international_runs
                                from (
                                    (select batter, sum(batter_runs) as total_runs from odi_deliveries
                                    group by batter)
                                    union all
                                    (select batter, sum(batter_runs) as total_runs from t20_deliveries
                                    group by batter)
                                    union all  
                                    (select batter, sum(batter_runs) as total_runs from test_deliveries
                                    group by batter)
                                    ) as inter_match
                                group by batter having international_runs>=10000;
                    '''
            cursor.execute(query)
            final_query= '''
                            select im.player, im.international_runs, ipl.num_of_ipl_matches
                            from inter_matches im
                            join (
                                    select player, count(match_id) as num_of_ipl_matches 
                                    from ipl_players
                                    group by  player having num_of_ipl_matches>=100
                                ) as ipl
                                on im.player=ipl.player
                            order by im.international_runs desc,ipl.num_of_ipl_matches desc;
                        '''
            cursor.execute(final_query)
            result = cursor.fetchall()
            st.write(pd.DataFrame(result))

with st.expander("**09. 🧤 Top 10 Fielders by Catches Taken Across All Matches**"):
    query = '''
                select fielder_1 as fielder, sum(total_catches) as total_catches
                from (
                    (select fielder_1, count(*) as total_catches
                    from ipl_deliveries
                    where wicket="caught" and fielder_1 is not null
                    group by fielder_1)
                    union all
                    (select fielder_1, count(*) as total_catches
                    from odi_deliveries
                    where wicket="caught" and fielder_1 is not null
                    group by fielder_1)
                    union all
                    (select fielder_1, count(*) as total_catches
                    from t20_deliveries
                    where wicket="caught" and fielder_1 is not null
                    group by fielder_1)
                    union all
                    (select fielder_1, count(*) as total_catches
                    from test_deliveries
                    where wicket="caught" and fielder_1 is not null
                    group by fielder_1)
                    ) as catches
                group by fielder order by total_catches desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**10. ⛔ Top 10 Bowlers with Most Maidens Across All Matches**"):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        with cursor:
            queries = ['''
                        create temporary table if not exists ipl_maiden
                            select match_id, inning, bowler, over_number 
                            from ipl_deliveries
                            group by match_id, inning, over_number, bowler 
                            having sum(runs)=0;
                    ''',
                    '''
                        create temporary table if not exists odi_maiden
                            select match_id, inning, bowler, over_number 
                            from odi_deliveries
                            group by match_id,inning, over_number, bowler 
                            having sum(runs)=0;
                        ''',
                        '''
                        create temporary table if not exists t20_maiden
                            select match_id, inning, bowler, over_number 
                            from t20_deliveries
                            group by match_id,inning, over_number, bowler 
                            having sum(runs)=0;
                        ''',
                        '''
                        create temporary table if not exists test_maiden
                            select match_id, inning, bowler, over_number 
                            from test_deliveries
                            group by match_id,inning, over_number, bowler 
                            having sum(runs)=0;
                        ''']
            for q in queries:
                cursor.execute(q)
            
            final_query = '''
                            select bowler, count(*) as total_maiden_overs
                            from(
                                (select match_id,inning, bowler, over_number from ipl_maiden)
                                union all
                                (select match_id,inning, bowler, over_number from odi_maiden)
                                union all
                                (select match_id,inning, bowler, over_number from t20_maiden)
                                union all
                                (select match_id,inning, bowler, over_number from test_maiden)
                                ) as maiden
                            group by bowler 
                            order by total_maiden_overs desc limit 10;
                        '''
            cursor.execute(final_query)
            result = cursor.fetchall()
            st.write(pd.DataFrame(result))

with st.expander("**11. 💥 Most Sixes Hit in Combined Career Across All Matches**"):
    query = '''
                select batter, sum(total_sixes) as total_sixes
                from (
                    (select batter, count(*) as total_sixes
                    from ipl_deliveries
                    where batter_runs=6
                    group by batter)
                    union all
                    (select batter, count(*) as total_sixes
                    from odi_deliveries
                    where batter_runs=6
                    group by batter)
                    union all
                    (select batter, count(*) as total_sixes
                    from t20_deliveries
                    where batter_runs=6
                    group by batter)
                    union all
                    (select batter, count(*) as total_sixes
                    from test_deliveries
                    where batter_runs=6
                    group by batter)
                    ) as six_table
                group by batter 
                order by total_sixes desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**12. 🎯🎳 Bowlers with 5-Wicket Hauls in All Three International Formats**"):
    connection = get_connection()
    cursor = connection.cursor()
    with connection:
        with cursor:
            queries = ['''
                        create temporary table if not exists odi_five_wic_haul
                            select match_id, inning, bowler, count(wicket) as wickets
                            from odi_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler or fielder_4 = bowler))
                            group by match_id, inning, bowler 
                            having count(wicket)>=5;
                       ''',
                       '''
                        create temporary table if not exists t20_five_wic_haul
                            select match_id, inning, bowler, count(wicket) as wickets
                            from t20_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                            group by match_id, inning, bowler 
                            having count(wicket)>=5;
                        ''',
                        '''
                        create temporary table if not exists test_five_wic_haul
                            select match_id, inning, bowler, count(wicket) as wickets
                            from test_deliveries
                            where (wicket in ('caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket')) or
                                ((wicket is not null) or 
                                (fielder_1 = bowler or fielder_2 = bowler or fielder_3 = bowler))
                            group by match_id, inning, bowler 
                            having count(wicket)>=5; 
                        ''']
            for q in queries:
                cursor.execute(q)
            final_query = '''  
                            select odi.bowler,
                                odi.wickets as odi_five_wickets_hauls, 
                                t20.wickets as t20_five_wickets_hauls,
                                test.wickets as test_five_wickets_hauls,
                                (odi.wickets+t20.wickets+test.wickets) as total_five_wickets_hauls
                            from 
                                (select bowler,sum(wickets) as wickets from odi_five_wic_haul group by bowler) as odi
                                join (select bowler,sum(wickets) as wickets from t20_five_wic_haul group by bowler) 
                                    as t20 on odi.bowler=t20.bowler
                                join (select bowler,sum(wickets) as wickets from test_five_wic_haul group by bowler)
                                    as test on odi.bowler=test.bowler
                            order by total_five_wickets_hauls desc;
                          '''
            cursor.execute(final_query)
            result = cursor.fetchall()
            st.write(pd.DataFrame(result))

with st.expander("**13. 🚀 First Cricketer to Score a Century in IPL**"):
    query = '''
                select m.match_name, d.batter, sum(d.batter_runs) as runs,count(ball_number) as balls, m.start_date as date
                from ipl_deliveries d
                join ipl_matches m on d.match_id=m.match_id
                where d.extras not in ('wides', 'no_ball')  or d.extras IS NULL
                group by m.match_id, m.start_date, m.match_name, d.batter having sum(d.batter_runs)>=100
                order by m.start_date limit 1;
            '''
    st.write(run_query(query))

with st.expander("**14. 🎯💣 Players Who Hit Six Sixes in an Over (IPL)**"):
    query = '''
                select batter
                from ipl_deliveries
                where (extras not in ('wides', 'no_ball')) or (extras IS NULL)
                group by match_id, over_number, batter
                having sum(batter_runs)>=36;
            '''
    st.write(run_query(query))

with st.expander("**15. 🤝 Tied Matches (IPL, ODI, T20) – Full List**"):
    query = '''
                select * 
                from (
                    (select start_date as match_date, match_name, teams
                    from ipl_matches
                    where (match_name is not null) and (result = "tie"))
                    union all
                    (select start_date as match_date, match_name, teams
                    from odi_matches
                    where (match_name is not null) and (result = "tie"))
                    union all
                    (select start_date as match_date, match_name, teams
                    from t20_matches
                    where (match_name is not null) and (result = "tie"))
                    ) as tied_matches
                order by match_date;
            '''
    st.write(run_query(query))

with st.expander("**16. 🏁 Number of Matches Won by Each Team in International Matches**"):
    query = '''
                select odi.match_winner as team_name, odi.odi_matches, t20.t20_matches, test.test_matches
                from
                        (select match_winner, count(*) as odi_matches
                        from odi_matches
                        where match_winner is not null
                        group by match_winner)
                        as odi
                join
                        (select match_winner, count(*) as t20_matches
                        from t20_matches
                        where match_winner is not null
                        group by match_winner)
                        as t20 on odi.match_winner=t20.match_winner
                join        
                        (select match_winner, count(*) as test_matches
                        from test_matches
                        where match_winner is not null
                        group by match_winner)
                        as test on odi.match_winner=test.match_winner
                order by odi.odi_matches desc, t20.t20_matches desc, test.test_matches desc;
            '''
    st.write(run_query(query))

with st.expander("**17. 👑 Most Matches Played by a Player Across All Formats**"):
    query = '''
                select player, count(distinct match_id) as matches_played
                from (
                    select match_id, player from ipl_players
                    union all
                    select match_id, player from odi_players
                    union all
                    select match_id, player from t20_players
                    union all
                    select match_id, player from test_players
                    ) as all_players
                group by player
                order by matches_played desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**18. 🏟️ Top 10 Most Played Venues in International Matches**"):
    query = '''
                select venue, sum(total) as matches_played
                from (
                    select venue, count(*) as total from odi_matches group by venue
                    union all
                    select venue, count(*) as total from t20_matches group by venue
                    union all
                    select venue, count(*) as total from test_matches group by venue
                    ) as all_venues
                group by venue
                order by matches_played desc limit 10;
            '''
    st.write(run_query(query))

with st.expander("**19. ⚡ Best Strike Rates Across All Formats (Min 500 Runs)**"):
    query = '''
                select batter, 
                    sum(batter_runs) as total_runs, 
                    count(*) as total_balls,
                    (sum(batter_runs)*100.0/count(*)) as strike_rate
                from (
                    select batter, batter_runs from ipl_deliveries
                    where (extras not in ('wides', 'noballs')) or (extras IS NULL)
                    union all
                    select batter, batter_runs from odi_deliveries
                    where (extras not in ('wides', 'noballs')) or (extras IS NULL)
                    union all
                    select batter, batter_runs from t20_deliveries
                    where (extras not in ('wides', 'noballs')) or (extras IS NULL)
                    union all
                    select batter, batter_runs from test_deliveries
                    where (extras not in ('wides', 'noballs')) or (extras IS NULL)
                    ) as all_battings
                group by batter having sum(batter_runs) >= 500
                order by strike_rate desc limit 10;
            '''
    st.write(run_query(query))
 
with st.expander("**20. 🔼 Total Sixes by Player Across Formats**"):
    query = '''
                select batter, sum(sixes) as total_sixes
                from (
                    select batter, count(*) as sixes from ipl_deliveries where batter_runs=6 group by batter
                    union all
                    select batter, count(*) as sixes from odi_deliveries where batter_runs=6 group by batter
                    union all
                    select batter, count(*) as sixes from t20_deliveries where batter_runs=6 group by batter
                    union all
                    select batter, count(*) as sixes from test_deliveries where batter_runs=6 group by batter
                    ) as all_sixes
                group by batter    
                order by total_sixes desc limit 10;
            '''
    st.write(run_query(query)) 