--
-- PostgreSQL database dump
--

\restrict dgCt5Wiao4nhESbrgM0GjQgokAhHglngA7wNzWj88dF6NE1y2nTv3qvQeBkoCKc

-- Dumped from database version 9.6.1
-- Dumped by pg_dump version 9.6.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: alembic; Type: SCHEMA; Schema: -; Owner: www-data
--

CREATE SCHEMA alembic;


ALTER SCHEMA alembic OWNER TO "www-data";

--
-- Name: guidebook; Type: SCHEMA; Schema: -; Owner: www-data
--

CREATE SCHEMA guidebook;


ALTER SCHEMA guidebook OWNER TO "www-data";

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: sympa; Type: SCHEMA; Schema: -; Owner: www-data
--

CREATE SCHEMA sympa;


ALTER SCHEMA sympa OWNER TO "www-data";

--
-- Name: tiger; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger;


ALTER SCHEMA tiger OWNER TO postgres;

--
-- Name: tiger_data; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tiger_data;


ALTER SCHEMA tiger_data OWNER TO postgres;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- Name: tracking; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tracking;


ALTER SCHEMA tracking OWNER TO postgres;

--
-- Name: users; Type: SCHEMA; Schema: -; Owner: www-data
--

CREATE SCHEMA users;


ALTER SCHEMA users OWNER TO "www-data";

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: dblink; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS dblink WITH SCHEMA public;


--
-- Name: EXTENSION dblink; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION dblink IS 'connect to other PostgreSQL databases from within a database';


--
-- Name: fuzzystrmatch; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS fuzzystrmatch WITH SCHEMA public;


--
-- Name: EXTENSION fuzzystrmatch; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION fuzzystrmatch IS 'determine similarities and distance between strings';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: postgis_tiger_geocoder; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder WITH SCHEMA tiger;


--
-- Name: EXTENSION postgis_tiger_geocoder; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_tiger_geocoder IS 'PostGIS tiger geocoder and reverse geocoder';


--
-- Name: postgis_topology; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS postgis_topology WITH SCHEMA topology;


--
-- Name: EXTENSION postgis_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis_topology IS 'PostGIS topology spatial types and functions';


SET search_path = guidebook, pg_catalog;

--
-- Name: access_condition; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE access_condition AS ENUM (
    'cleared',
    'snowy',
    'closed_snow',
    'closed_cleared'
);


ALTER TYPE guidebook.access_condition OWNER TO "www-data";

--
-- Name: access_time_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE access_time_type AS ENUM (
    '1min',
    '5min',
    '10min',
    '15min',
    '20min',
    '30min',
    '45min',
    '1h',
    '1h30',
    '2h',
    '2h30',
    '3h',
    '3h+'
);


ALTER TYPE guidebook.access_time_type OWNER TO "www-data";

--
-- Name: activity_rate; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE activity_rate AS ENUM (
    'activity_rate_y5',
    'activity_rate_m2',
    'activity_rate_w1'
);


ALTER TYPE guidebook.activity_rate OWNER TO "www-data";

--
-- Name: activity_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE activity_type AS ENUM (
    'skitouring',
    'snow_ice_mixed',
    'mountain_climbing',
    'rock_climbing',
    'ice_climbing',
    'hiking',
    'snowshoeing',
    'paragliding',
    'mountain_biking',
    'via_ferrata',
    'slacklining'
);


ALTER TYPE guidebook.activity_type OWNER TO "www-data";

--
-- Name: aid_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE aid_rating AS ENUM (
    'A0',
    'A0+',
    'A1',
    'A1+',
    'A2',
    'A2+',
    'A3',
    'A3+',
    'A4',
    'A4+',
    'A5',
    'A5+'
);


ALTER TYPE guidebook.aid_rating OWNER TO "www-data";

--
-- Name: area_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE area_type AS ENUM (
    'range',
    'admin_limits',
    'country'
);


ALTER TYPE guidebook.area_type OWNER TO "www-data";

--
-- Name: article_category; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE article_category AS ENUM (
    'mountain_environment',
    'gear',
    'technical',
    'topoguide_supplements',
    'soft_mobility',
    'expeditions',
    'stories',
    'c2c_meetings',
    'tags',
    'site_info',
    'association'
);


ALTER TYPE guidebook.article_category OWNER TO "www-data";

--
-- Name: article_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE article_type AS ENUM (
    'collab',
    'personal'
);


ALTER TYPE guidebook.article_type OWNER TO "www-data";

--
-- Name: author_status; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE author_status AS ENUM (
    'primary_impacted',
    'secondary_impacted',
    'internal_witness',
    'external_witness'
);


ALTER TYPE guidebook.author_status OWNER TO "www-data";

--
-- Name: autonomy; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE autonomy AS ENUM (
    'non_autonomous',
    'autonomous',
    'expert'
);


ALTER TYPE guidebook.autonomy OWNER TO "www-data";

--
-- Name: avalanche_level; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE avalanche_level AS ENUM (
    'level_1',
    'level_2',
    'level_3',
    'level_4',
    'level_5',
    'level_na'
);


ALTER TYPE guidebook.avalanche_level OWNER TO "www-data";

--
-- Name: avalanche_signs; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE avalanche_signs AS ENUM (
    'no',
    'danger_sign',
    'recent_avalanche',
    'natural_avalanche',
    'accidental_avalanche'
);


ALTER TYPE guidebook.avalanche_signs OWNER TO "www-data";

--
-- Name: avalanche_slope; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE avalanche_slope AS ENUM (
    'slope_lt_30',
    'slope_30_35',
    'slope_35_40',
    'slope_40_45',
    'slope_gt_45'
);


ALTER TYPE guidebook.avalanche_slope OWNER TO "www-data";

--
-- Name: book_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE book_type AS ENUM (
    'topo',
    'environment',
    'historical',
    'biography',
    'photos-art',
    'novel',
    'technics',
    'tourism',
    'magazine'
);


ALTER TYPE guidebook.book_type OWNER TO "www-data";

--
-- Name: children_proof_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE children_proof_type AS ENUM (
    'very_safe',
    'safe',
    'dangerous',
    'very_dangerous'
);


ALTER TYPE guidebook.children_proof_type OWNER TO "www-data";

--
-- Name: climbing_indoor_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE climbing_indoor_type AS ENUM (
    'pitch',
    'bloc'
);


ALTER TYPE guidebook.climbing_indoor_type OWNER TO "www-data";

--
-- Name: climbing_outdoor_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE climbing_outdoor_type AS ENUM (
    'single',
    'multi',
    'bloc',
    'psicobloc'
);


ALTER TYPE guidebook.climbing_outdoor_type OWNER TO "www-data";

--
-- Name: climbing_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE climbing_rating AS ENUM (
    '2',
    '3a',
    '3b',
    '3c',
    '4a',
    '4b',
    '4c',
    '5a',
    '5a+',
    '5b',
    '5b+',
    '5c',
    '5c+',
    '6a',
    '6a+',
    '6b',
    '6b+',
    '6c',
    '6c+',
    '7a',
    '7a+',
    '7b',
    '7b+',
    '7c',
    '7c+',
    '8a',
    '8a+',
    '8b',
    '8b+',
    '8c',
    '8c+',
    '9a',
    '9a+',
    '9b',
    '9b+',
    '9c',
    '9c+'
);


ALTER TYPE guidebook.climbing_rating OWNER TO "www-data";

--
-- Name: climbing_style; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE climbing_style AS ENUM (
    'slab',
    'vertical',
    'overhang',
    'roof',
    'small_pillar',
    'crack_dihedral'
);


ALTER TYPE guidebook.climbing_style OWNER TO "www-data";

--
-- Name: condition_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE condition_rating AS ENUM (
    'excellent',
    'good',
    'average',
    'poor',
    'awful'
);


ALTER TYPE guidebook.condition_rating OWNER TO "www-data";

--
-- Name: custodianship_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE custodianship_type AS ENUM (
    'accessible_when_wardened',
    'always_accessible',
    'key_needed',
    'no_warden'
);


ALTER TYPE guidebook.custodianship_type OWNER TO "www-data";

--
-- Name: engagement_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE engagement_rating AS ENUM (
    'I',
    'II',
    'III',
    'IV',
    'V',
    'VI'
);


ALTER TYPE guidebook.engagement_rating OWNER TO "www-data";

--
-- Name: equipment_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE equipment_rating AS ENUM (
    'P1',
    'P1+',
    'P2',
    'P2+',
    'P3',
    'P3+',
    'P4',
    'P4+'
);


ALTER TYPE guidebook.equipment_rating OWNER TO "www-data";

--
-- Name: event_activity_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE event_activity_type AS ENUM (
    'sport_climbing',
    'multipitch_climbing',
    'alpine_climbing',
    'snow_ice_mixed',
    'ice_climbing',
    'skitouring',
    'other'
);


ALTER TYPE guidebook.event_activity_type OWNER TO "www-data";

--
-- Name: event_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE event_type AS ENUM (
    'avalanche',
    'stone_ice_fall',
    'ice_cornice_collapse',
    'person_fall',
    'crevasse_fall',
    'physical_failure',
    'injury_without_fall',
    'blocked_person',
    'weather_event',
    'safety_operation',
    'critical_situation',
    'other'
);


ALTER TYPE guidebook.event_type OWNER TO "www-data";

--
-- Name: exposition_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE exposition_rating AS ENUM (
    'E1',
    'E2',
    'E3',
    'E4'
);


ALTER TYPE guidebook.exposition_rating OWNER TO "www-data";

--
-- Name: exposition_rock_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE exposition_rock_rating AS ENUM (
    'E1',
    'E2',
    'E3',
    'E4',
    'E5',
    'E6'
);


ALTER TYPE guidebook.exposition_rock_rating OWNER TO "www-data";

--
-- Name: feed_change_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE feed_change_type AS ENUM (
    'created',
    'updated',
    'added_photos'
);


ALTER TYPE guidebook.feed_change_type OWNER TO "www-data";

--
-- Name: frequentation_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE frequentation_type AS ENUM (
    'quiet',
    'some',
    'crowded',
    'overcrowded'
);


ALTER TYPE guidebook.frequentation_type OWNER TO "www-data";

--
-- Name: gender; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE gender AS ENUM (
    'male',
    'female'
);


ALTER TYPE guidebook.gender OWNER TO "www-data";

--
-- Name: glacier_gear_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE glacier_gear_type AS ENUM (
    'no',
    'glacier_safety_gear',
    'crampons_spring',
    'crampons_req',
    'glacier_crampons'
);


ALTER TYPE guidebook.glacier_gear_type OWNER TO "www-data";

--
-- Name: glacier_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE glacier_rating AS ENUM (
    'easy',
    'possible',
    'difficult',
    'impossible'
);


ALTER TYPE guidebook.glacier_rating OWNER TO "www-data";

--
-- Name: global_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE global_rating AS ENUM (
    'F',
    'F+',
    'PD-',
    'PD',
    'PD+',
    'AD-',
    'AD',
    'AD+',
    'D-',
    'D',
    'D+',
    'TD-',
    'TD',
    'TD+',
    'ED-',
    'ED',
    'ED+',
    'ED4',
    'ED5',
    'ED6',
    'ED7'
);


ALTER TYPE guidebook.global_rating OWNER TO "www-data";

--
-- Name: ground_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE ground_type AS ENUM (
    'prairie',
    'scree',
    'snow'
);


ALTER TYPE guidebook.ground_type OWNER TO "www-data";

--
-- Name: hiking_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE hiking_rating AS ENUM (
    'T1',
    'T2',
    'T3',
    'T4',
    'T5'
);


ALTER TYPE guidebook.hiking_rating OWNER TO "www-data";

--
-- Name: hut_status; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE hut_status AS ENUM (
    'open_guarded',
    'open_non_guarded',
    'closed_hut'
);


ALTER TYPE guidebook.hut_status OWNER TO "www-data";

--
-- Name: ice_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE ice_rating AS ENUM (
    '1',
    '2',
    '3',
    '3+',
    '4',
    '4+',
    '5',
    '5+',
    '6',
    '6+',
    '7',
    '7+'
);


ALTER TYPE guidebook.ice_rating OWNER TO "www-data";

--
-- Name: image_category; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE image_category AS ENUM (
    'landscapes',
    'detail',
    'action',
    'track',
    'rise',
    'descent',
    'topo',
    'people',
    'fauna',
    'flora',
    'nivology',
    'geology',
    'hut',
    'equipment',
    'book',
    'help',
    'misc'
);


ALTER TYPE guidebook.image_category OWNER TO "www-data";

--
-- Name: image_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE image_type AS ENUM (
    'collaborative',
    'personal',
    'copyright'
);


ALTER TYPE guidebook.image_type OWNER TO "www-data";

--
-- Name: labande_ski_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE labande_ski_rating AS ENUM (
    'S1',
    'S2',
    'S3',
    'S4',
    'S5',
    'S6',
    'S7'
);


ALTER TYPE guidebook.labande_ski_rating OWNER TO "www-data";

--
-- Name: lang; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE lang AS ENUM (
    'fr',
    'it',
    'de',
    'en',
    'es',
    'ca',
    'eu',
    'sl',
    'zh'
);


ALTER TYPE guidebook.lang OWNER TO "www-data";

--
-- Name: lift_status; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE lift_status AS ENUM (
    'open',
    'closed'
);


ALTER TYPE guidebook.lift_status OWNER TO "www-data";

--
-- Name: map_editor; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE map_editor AS ENUM (
    'IGN',
    'Swisstopo',
    'Escursionista'
);


ALTER TYPE guidebook.map_editor OWNER TO "www-data";

--
-- Name: map_scale; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE map_scale AS ENUM (
    '25000',
    '50000',
    '100000'
);


ALTER TYPE guidebook.map_scale OWNER TO "www-data";

--
-- Name: mixed_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE mixed_rating AS ENUM (
    'M1',
    'M2',
    'M3',
    'M3+',
    'M4',
    'M4+',
    'M5',
    'M5+',
    'M6',
    'M6+',
    'M7',
    'M7+',
    'M8',
    'M8+',
    'M9',
    'M9+',
    'M10',
    'M10+',
    'M11',
    'M11+',
    'M12',
    'M12+'
);


ALTER TYPE guidebook.mixed_rating OWNER TO "www-data";

--
-- Name: month_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE month_type AS ENUM (
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec'
);


ALTER TYPE guidebook.month_type OWNER TO "www-data";

--
-- Name: mtb_down_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE mtb_down_rating AS ENUM (
    'V1',
    'V2',
    'V3',
    'V4',
    'V5'
);


ALTER TYPE guidebook.mtb_down_rating OWNER TO "www-data";

--
-- Name: mtb_up_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE mtb_up_rating AS ENUM (
    'M1',
    'M2',
    'M3',
    'M4',
    'M5'
);


ALTER TYPE guidebook.mtb_up_rating OWNER TO "www-data";

--
-- Name: orientation_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE orientation_type AS ENUM (
    'N',
    'NE',
    'E',
    'SE',
    'S',
    'SW',
    'W',
    'NW'
);


ALTER TYPE guidebook.orientation_type OWNER TO "www-data";

--
-- Name: paragliding_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE paragliding_rating AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5'
);


ALTER TYPE guidebook.paragliding_rating OWNER TO "www-data";

--
-- Name: parking_fee_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE parking_fee_type AS ENUM (
    'yes',
    'seasonal',
    'no'
);


ALTER TYPE guidebook.parking_fee_type OWNER TO "www-data";

--
-- Name: previous_injuries; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE previous_injuries AS ENUM (
    'no',
    'previous_injuries_2',
    'previous_injuries_3'
);


ALTER TYPE guidebook.previous_injuries OWNER TO "www-data";

--
-- Name: product_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE product_type AS ENUM (
    'farm_sale',
    'restaurant',
    'grocery',
    'bar',
    'sport_shop'
);


ALTER TYPE guidebook.product_type OWNER TO "www-data";

--
-- Name: public_transportation_ratings; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE public_transportation_ratings AS ENUM (
    'good service',
    'seasonal service',
    'poor service',
    'nearby service',
    'unknown service',
    'no service'
);


ALTER TYPE guidebook.public_transportation_ratings OWNER TO "www-data";

--
-- Name: public_transportation_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE public_transportation_type AS ENUM (
    'train',
    'bus',
    'service_on_demand',
    'boat'
);


ALTER TYPE guidebook.public_transportation_type OWNER TO "www-data";

--
-- Name: qualification_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE qualification_type AS ENUM (
    'federal_supervisor',
    'federal_trainer',
    'professional_diploma'
);


ALTER TYPE guidebook.qualification_type OWNER TO "www-data";

--
-- Name: quality_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE quality_type AS ENUM (
    'empty',
    'draft',
    'medium',
    'fine',
    'great'
);


ALTER TYPE guidebook.quality_type OWNER TO "www-data";

--
-- Name: rain_proof_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE rain_proof_type AS ENUM (
    'exposed',
    'partly_protected',
    'protected',
    'inside'
);


ALTER TYPE guidebook.rain_proof_type OWNER TO "www-data";

--
-- Name: risk_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE risk_rating AS ENUM (
    'X1',
    'X2',
    'X3',
    'X4',
    'X5'
);


ALTER TYPE guidebook.risk_rating OWNER TO "www-data";

--
-- Name: rock_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE rock_type AS ENUM (
    'basalte',
    'calcaire',
    'conglomerat',
    'craie',
    'gneiss',
    'gres',
    'granit',
    'migmatite',
    'mollasse_calcaire',
    'pouding',
    'quartzite',
    'rhyolite',
    'schiste',
    'trachyte',
    'artificial'
);


ALTER TYPE guidebook.rock_type OWNER TO "www-data";

--
-- Name: route_configuration_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE route_configuration_type AS ENUM (
    'edge',
    'pillar',
    'face',
    'corridor',
    'goulotte',
    'glacier'
);


ALTER TYPE guidebook.route_configuration_type OWNER TO "www-data";

--
-- Name: route_duration_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE route_duration_type AS ENUM (
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    '10',
    '10+'
);


ALTER TYPE guidebook.route_duration_type OWNER TO "www-data";

--
-- Name: route_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE route_type AS ENUM (
    'return_same_way',
    'loop',
    'loop_hut',
    'traverse',
    'raid',
    'expedition'
);


ALTER TYPE guidebook.route_type OWNER TO "www-data";

--
-- Name: severity; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE severity AS ENUM (
    'severity_no',
    '1d_to_3d',
    '4d_to_1m',
    '1m_to_3m',
    'more_than_3m'
);


ALTER TYPE guidebook.severity OWNER TO "www-data";

--
-- Name: ski_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE ski_rating AS ENUM (
    '1.1',
    '1.2',
    '1.3',
    '2.1',
    '2.2',
    '2.3',
    '3.1',
    '3.2',
    '3.3',
    '4.1',
    '4.2',
    '4.3',
    '5.1',
    '5.2',
    '5.3',
    '5.4',
    '5.5',
    '5.6'
);


ALTER TYPE guidebook.ski_rating OWNER TO "www-data";

--
-- Name: slackline_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE slackline_type AS ENUM (
    'slackline',
    'highline',
    'waterline'
);


ALTER TYPE guidebook.slackline_type OWNER TO "www-data";

--
-- Name: snow_clearance_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE snow_clearance_rating AS ENUM (
    'often',
    'sometimes',
    'progressive',
    'naturally',
    'closed_in_winter',
    'non_applicable'
);


ALTER TYPE guidebook.snow_clearance_rating OWNER TO "www-data";

--
-- Name: snowshoe_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE snowshoe_rating AS ENUM (
    'R1',
    'R2',
    'R3',
    'R4',
    'R5'
);


ALTER TYPE guidebook.snowshoe_rating OWNER TO "www-data";

--
-- Name: supervision_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE supervision_type AS ENUM (
    'no_supervision',
    'federal_supervision',
    'professional_supervision'
);


ALTER TYPE guidebook.supervision_type OWNER TO "www-data";

--
-- Name: user_category; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE user_category AS ENUM (
    'amateur',
    'mountain_guide',
    'mountain_leader',
    'ski_instructor',
    'climbing_instructor',
    'mountainbike_instructor',
    'paragliding_instructor',
    'hut_warden',
    'ski_patroller',
    'avalanche_forecaster',
    'club',
    'institution'
);


ALTER TYPE guidebook.user_category OWNER TO "www-data";

--
-- Name: via_ferrata_rating; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE via_ferrata_rating AS ENUM (
    'K1',
    'K2',
    'K3',
    'K4',
    'K5',
    'K6'
);


ALTER TYPE guidebook.via_ferrata_rating OWNER TO "www-data";

--
-- Name: waypoint_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE waypoint_type AS ENUM (
    'summit',
    'pass',
    'lake',
    'waterfall',
    'locality',
    'bisse',
    'canyon',
    'access',
    'climbing_outdoor',
    'climbing_indoor',
    'hut',
    'gite',
    'shelter',
    'bivouac',
    'camp_site',
    'base_camp',
    'local_product',
    'paragliding_takeoff',
    'paragliding_landing',
    'cave',
    'waterpoint',
    'weather_station',
    'webcam',
    'virtual',
    'misc',
    'slackline_spot'
);


ALTER TYPE guidebook.waypoint_type OWNER TO "www-data";

--
-- Name: weather_station_type; Type: TYPE; Schema: guidebook; Owner: www-data
--

CREATE TYPE weather_station_type AS ENUM (
    'temperature',
    'wind_speed',
    'wind_direction',
    'humidity',
    'pressure',
    'precipitation',
    'precipitation_heater',
    'snow_height',
    'insolation'
);


ALTER TYPE guidebook.weather_station_type OWNER TO "www-data";

--
-- Name: calculate_duration(activity_type[], integer, smallint, smallint, smallint, smallint); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION calculate_duration(activities activity_type[], route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint DEFAULT NULL::smallint, access_height smallint DEFAULT NULL::smallint) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    activity guidebook.activity_type;
    duration float;
    min_duration float := NULL;
BEGIN
    -- Pour chaque activité, calculer la durée et garder la plus courte
    FOREACH activity IN ARRAY activities LOOP
        duration := guidebook.calculate_duration(
            activity, route_length, height_diff_up, height_diff_down, 
            difficulties_height, access_height
        );
        
        -- Si cette durée est valide et plus courte que la précédente (ou c'est la première)
        IF duration IS NOT NULL AND (min_duration IS NULL OR duration < min_duration) THEN
            min_duration := duration;
        END IF;
    END LOOP;
    
    RETURN min_duration;
END;
$$;


ALTER FUNCTION guidebook.calculate_duration(activities activity_type[], route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint, access_height smallint) OWNER TO "www-data";

--
-- Name: calculate_duration(activity_type, integer, smallint, smallint, smallint, smallint); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION calculate_duration(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint DEFAULT NULL::smallint, access_height smallint DEFAULT NULL::smallint) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    is_climbing boolean;
BEGIN
    -- Déterminer si c'est un itinéraire de grimpe
    is_climbing := activity IN ('rock_climbing', 'mountain_climbing', 'ice_climbing', 
                                'snow_ice_mixed', 'paragliding', 'slacklining', 'via_ferrata');
    
    IF is_climbing THEN
        RETURN guidebook.calculate_duration_climbing(
            activity, route_length, height_diff_up, height_diff_down, 
            difficulties_height, access_height
        );
    ELSE
        RETURN guidebook.calculate_duration_non_climbing(
            activity, route_length, height_diff_up, height_diff_down
        );
    END IF;
END;
$$;


ALTER FUNCTION guidebook.calculate_duration(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint, access_height smallint) OWNER TO "www-data";

--
-- Name: calculate_duration_climbing(activity_type, integer, smallint, smallint, smallint, smallint); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION calculate_duration_climbing(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint DEFAULT NULL::smallint, access_height smallint DEFAULT NULL::smallint) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    h float;
    dp float;
    dn float;
    d_diff float;
    d_app float;     -- Dénivelé de l'approche
    t_diff float;    -- Temps des difficultés
    t_app float;     -- Temps de l'approche
    dh_app float;    -- Composante horizontale de l'approche
    dv_app float;    -- Composante verticale de l'approche
    v_diff float := 50.0; -- Vitesse ascensionnelle des difficultés (m/h)

    -- Paramètres pour l'approche (randonnée selon le cadrage)
    v float := 5.0;    -- km/h (vitesse horizontale)
    a float := 300.0;  -- m/h (montée)
    d float := 500.0;  -- m/h (descente)

    min_duration_hours float := 0.5; -- 30 minutes
    max_duration_hours float := 18.0; -- 18 heures
    dm float; -- Durée totale en heures
BEGIN
    -- Vérifier que c'est bien un itinéraire grimpant
    IF NOT (activity IN ('rock_climbing', 'mountain_climbing', 'ice_climbing',
                        'snow_ice_mixed', 'paragliding', 'slacklining', 'via_ferrata')) THEN
        RETURN NULL;
    END IF;

    -- Gestion de la règle: si dénivelé négatif absent, égaler au positif
    IF height_diff_down IS NULL AND height_diff_up IS NOT NULL THEN
        dn := height_diff_up::float;
    ELSE
        dn := COALESCE(height_diff_down::float, 0);
    END IF;

    -- Convertir les autres valeurs
    h := COALESCE(route_length::float / 1000, 0); -- Convertir la longueur de l'itinéraire en km
    dp := COALESCE(height_diff_up::float, 0);     -- Dénivelé positif total

    -- CAS 1: Le dénivelé des difficultés n'est pas renseigné
    IF difficulties_height IS NULL OR difficulties_height <= 0 THEN
        -- "on considère que tout l'Itinéraire est grimpant et sans approche"
        -- "Dg = dTotal / vDiff"
        IF dp <= 0 THEN
            RETURN NULL; -- Pas de données utilisables pour le calcul
        END IF;

        dm := dp / v_diff;

        -- Validation des bornes de cohérence
        IF dm < min_duration_hours OR dm > max_duration_hours THEN
            RETURN NULL;
        END IF;

        RETURN dm / 24.0; -- Convertir en jours
    END IF;

    -- CAS 2: Le dénivelé des difficultés est renseigné
    d_diff := difficulties_height::float;

    -- Vérification de cohérence basique
    IF dp > 0 AND d_diff > dp THEN
        RETURN NULL; -- Dénivelé des difficultés > dénivelé total = incohérent
    END IF;

    -- Calcul du temps des difficultés
    -- "tDiff = dDiff/vDiff"
    t_diff := d_diff / v_diff;

    -- Calcul du dénivelé de l'approche
    -- Dans cette version, 'd_app' est toujours 'dTotal - dDiff',
    -- ignorant le paramètre 'access_height' pour cette partie du calcul.
    d_app := GREATEST(dp - d_diff, 0);

    -- Calcul du temps d'approche
    IF d_app > 0 THEN
        -- "calculée de la même façon que pour la Durée de parcours de l'itinéraire à pied"
        -- "mais avec le dénivelé dApp de l'approche à la place du dénivelé total"

        dh_app := h / v;                    -- Composante horizontale de l'approche
        dv_app := (d_app / a) + (d_app / d);   -- Composante verticale de l'approche (montée + descente)

        -- Appliquer la formule DIN 33466 pour le temps d'approche
        IF dh_app < dv_app THEN
            t_app := dv_app + (dh_app / 2);
        ELSE
            t_app := (dv_app / 2) + dh_app;
        END IF;
    ELSE
        t_app := 0; -- Pas de dénivelé d'approche, donc temps d'approche nul
    END IF;

    -- Calcul final selon le cadrage
    -- "Dg = max(tDiff ,tApp) + 0,5 min(tDiff, tApp)"
    dm := GREATEST(t_diff, t_app) + 0.5 * LEAST(t_diff, t_app);

    -- Validation des bornes de cohérence
    IF dm < min_duration_hours OR dm > max_duration_hours THEN
        RETURN NULL;
    END IF;

    -- Convertir en jours (la fonction retourne des jours, mais le calcul est en heures)
    RETURN dm / 24.0;
END;
$$;


ALTER FUNCTION guidebook.calculate_duration_climbing(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint, difficulties_height smallint, access_height smallint) OWNER TO "www-data";

--
-- Name: calculate_duration_non_climbing(activity_type, integer, smallint, smallint); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION calculate_duration_non_climbing(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint) RETURNS double precision
    LANGUAGE plpgsql
    AS $$
DECLARE
    h float;
    dp float;
    dn float;
    v float;
    a float;
    d float;
    dh float;
    dv float;
    dm float;
    min_duration_hours float := 0.5; -- 30 minutes
    max_duration_hours float := 18.0; -- 18 heures
BEGIN
    -- Gestion de la règle: si dénivelé négatif absent, égaler au positif
    IF height_diff_down IS NULL AND height_diff_up IS NOT NULL THEN
        dn := height_diff_up::float;
    ELSE
        dn := COALESCE(height_diff_down::float, 0);
    END IF;
    
    -- Convertir les autres valeurs (remplacer NULL par 0)
    h := COALESCE(route_length::float / 1000, 0);
    dp := COALESCE(height_diff_up::float, 0);
    
    -- Définir les paramètres selon l'activité (selon le cadrage)
    IF activity = 'hiking' THEN
        v := 5.0; a := 300.0; d := 500.0;
    ELSIF activity = 'snowshoeing' THEN
        v := 4.5; a := 250.0; d := 400.0;
    ELSIF activity = 'skitouring' THEN
        v := 5.0; a := 300.0; d := 1500.0;
    ELSIF activity = 'mountain_biking' THEN
        v := 15.0; a := 250.0; d := 1000.0;
    ELSE
        -- Valeurs par défaut (randonnée)
        v := 5.0; a := 300.0; d := 500.0;
    END IF;
    
    -- Calcul selon la formule DIN 33466
    dh := h / v;                    -- Composante horizontale
    dv := (dp / a) + (dn / d);      -- Composante verticale
    
    -- Application de la formule
    IF dh < dv THEN
        dm := dv + (dh / 2);
    ELSE
        dm := (dv / 2) + dh;
    END IF;
    
    -- Validation des bornes de cohérence
    IF dm < min_duration_hours OR dm > max_duration_hours THEN
        RETURN NULL;
    END IF;
    
    -- Convertir en jours
    RETURN dm / 24.0;
END;
$$;


ALTER FUNCTION guidebook.calculate_duration_non_climbing(activity activity_type, route_length integer, height_diff_up smallint, height_diff_down smallint) OWNER TO "www-data";

--
-- Name: check_feed_area_ids(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION check_feed_area_ids() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- check area ids
  PERFORM change_id from guidebook.feed_document_changes
    where area_ids @> ARRAY[OLD.document_id] limit 1;
  IF FOUND THEN
    RAISE EXCEPTION 'Row in feed_document_changes still references area id %', OLD.document_id;
  END IF;
  RETURN null;
END;
$$;


ALTER FUNCTION guidebook.check_feed_area_ids() OWNER TO "www-data";

--
-- Name: check_feed_ids(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION check_feed_ids() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  user_id int;
  area_id int;
BEGIN
  -- check user ids
  FOREACH user_id IN ARRAY new.user_ids LOOP
    PERFORM id from users.user where id = user_id;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'Invalid user id: %', user_id;
    END IF;
  END LOOP;
  -- check area ids
  FOREACH area_id IN ARRAY new.area_ids LOOP
    PERFORM document_id from guidebook.areas where document_id = area_id;
    IF NOT FOUND THEN
      RAISE EXCEPTION 'Invalid area id: %', area_id;
    END IF;
  END LOOP;
  RETURN null;
END;
$$;


ALTER FUNCTION guidebook.check_feed_ids() OWNER TO "www-data";

--
-- Name: check_feed_user_ids(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION check_feed_user_ids() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- check user ids
  PERFORM change_id from guidebook.feed_document_changes
    where user_ids @> ARRAY[OLD.id] limit 1;
  IF FOUND THEN
    RAISE EXCEPTION 'Row in feed_document_changes still references user id %', OLD.id;
  END IF;
  RETURN null;
END;
$$;


ALTER FUNCTION guidebook.check_feed_user_ids() OWNER TO "www-data";

--
-- Name: create_cache_version(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION create_cache_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO
        guidebook.cache_versions(document_id)
        VALUES(new.document_id);
    RETURN null;
END;
$$;


ALTER FUNCTION guidebook.create_cache_version() OWNER TO "www-data";

--
-- Name: get_waypoints_for_routes(integer[]); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION get_waypoints_for_routes(p_route_ids integer[]) RETURNS TABLE(waypoint_id integer)
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- given an array of route ids, return all linked waypoints, parent waypoints
  -- of these waypoints and the grand-parents of these waypoints
  RETURN QUERY with routes as (
    select route_id from unnest(p_route_ids) as route_id ),
  linked_waypoints as (
    select a.parent_document_id as t_waypoint_id
    from routes r join guidebook.associations a
    on r.route_id = a.child_document_id and a.parent_document_type = 'w'),
  waypoint_parents as (
    select a.parent_document_id as t_waypoint_id
    from linked_waypoints w join guidebook.associations a
    on a.child_document_id = w.t_waypoint_id and a.parent_document_type = 'w'),
  waypoint_grandparents as (
    select a.parent_document_id as t_waypoint_id
    from waypoint_parents w join guidebook.associations a
    on a.child_document_id = w.t_waypoint_id and a.parent_document_type = 'w')
  select t_waypoint_id as waypoint_id
    from linked_waypoints
    union select t_waypoint_id from waypoint_parents
    union select t_waypoint_id from waypoint_grandparents;
END;
$$;


ALTER FUNCTION guidebook.get_waypoints_for_routes(p_route_ids integer[]) OWNER TO "www-data";

--
-- Name: increment_cache_version(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION increment_cache_version(p_document_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE guidebook.cache_versions v SET version = version + 1
  WHERE v.document_id = p_document_id;
END;
$$;


ALTER FUNCTION guidebook.increment_cache_version(p_document_id integer) OWNER TO "www-data";

--
-- Name: increment_cache_versions(integer[]); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION increment_cache_versions(p_document_ids integer[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  PERFORM guidebook.increment_cache_version(document_id)
  from unnest(p_document_ids) as document_id;
END;
$$;


ALTER FUNCTION guidebook.increment_cache_versions(p_document_ids integer[]) OWNER TO "www-data";

--
-- Name: simplify_geom_detail(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION simplify_geom_detail() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
  document_type varchar;
BEGIN
  IF new.geom_detail is not null THEN
    SELECT type from guidebook.documents where document_id = new.document_id
        INTO STRICT document_type;
    IF document_type in ('r', 'o') THEN
      new.geom_detail := ST_Simplify(new.geom_detail, 5);
    END IF;
  END IF;
  RETURN new;
END;
$$;


ALTER FUNCTION guidebook.simplify_geom_detail() OWNER TO "www-data";

--
-- Name: update_cache_version(integer, character varying); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version(p_document_id integer, p_document_type character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- function to update all dependent documents if a document changes

  -- update the version of the document itself
  PERFORM guidebook.increment_cache_version(p_document_id);

  -- update the version of linked documents (direct associations)
  PERFORM guidebook.update_cache_version_of_linked_documents(p_document_id);

  if p_document_type = 'w' then
    -- if the document is a waypoint, routes that this waypoint is
    -- main-waypoint of have to be updated.
    PERFORM guidebook.update_cache_version_of_main_waypoint_routes(p_document_id); --  # noqa: E501
  elsif p_document_type = 'r' then
     -- if the document is a route, associated waypoints (and their parent and
     -- grand-parents) have to be updated
    PERFORM guidebook.update_cache_version_of_route(p_document_id);
  elsif p_document_type = 'o' then
     -- if the document is an outing, associated waypoints of associates routes
     -- (and their parent and grand-parent waypoints) have to be updated
    PERFORM guidebook.update_cache_version_of_outing(p_document_id);
  elsif p_document_type = 'u' then
     -- if the document is an user profile, all documents that this user has
     -- edited have to be updated (to refresh the user name)
    PERFORM guidebook.update_cache_version_for_user(p_document_id);
  end if;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version(p_document_id integer, p_document_type character varying) OWNER TO "www-data";

--
-- Name: update_cache_version_for_area(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_for_area(p_area_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- function to update all documents that are associated with the given area
  with v as (
    select aa.document_id as document_id
    from guidebook.area_associations aa
    where aa.area_id = p_area_id
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.document_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_for_area(p_area_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_for_map(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_for_map(p_map_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- function to update all documents that are associated with the given map
  with v as (
    select ma.document_id as document_id
    from guidebook.map_associations ma
    where ma.topo_map_id = p_map_id
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.document_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_for_map(p_map_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_for_user(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_for_user(p_user_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- function to update all documents that the given user edited
  with v as (
    select dv.document_id as document_id
    from guidebook.documents_versions dv
      inner join guidebook.history_metadata h
    on dv.history_metadata_id = h.id
    where h.user_id = p_user_id
    group by dv.document_id
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.document_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_for_user(p_user_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_of_linked_documents(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_linked_documents(p_document_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  with v as (
    select a.parent_document_id as document_id
      from guidebook.associations a
      where a.child_document_id = p_document_id
    union (select b.child_document_id as document_id
      from guidebook.associations b
      where b.parent_document_id = p_document_id)
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.document_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_linked_documents(p_document_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_of_main_waypoint_routes(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_main_waypoint_routes(p_waypoint_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  with v as (
    select guidebook.get_waypoints_for_routes(array_agg(document_id)) as waypoint_id --  # noqa: E501
    from guidebook.routes
    where main_waypoint_id = p_waypoint_id
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.waypoint_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_main_waypoint_routes(p_waypoint_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_of_outing(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_outing(p_outing_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  with v as (
    select guidebook.get_waypoints_for_routes(array_agg(a.parent_document_id)) as waypoint_id --   # noqa: E501
    from guidebook.associations a
    where a.child_document_id = p_outing_id and a.parent_document_type = 'r'
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.waypoint_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_outing(p_outing_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_of_route(integer); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_route(p_route_id integer) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  with v as (
    select guidebook.get_waypoints_for_routes(ARRAY[p_route_id]) as waypoint_id
  )
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.waypoint_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_route(p_route_id integer) OWNER TO "www-data";

--
-- Name: update_cache_version_of_routes(integer[]); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_routes(p_route_ids integer[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- update the cache versions of waypoints (and the parent and grand-parent
  -- waypoints) associated to the given routes.
  PERFORM guidebook.update_cache_version_of_route(route_id)
  from unnest(p_route_ids) as route_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_routes(p_route_ids integer[]) OWNER TO "www-data";

--
-- Name: update_cache_version_of_waypoints(integer[]); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_of_waypoints(p_waypoints_ids integer[]) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
  -- update the cache versions of the parent and grand-parent waypoints
  -- of the given waypoints.
  with waypoints as (
    select waypoint_id from unnest(p_waypoints_ids) as waypoint_id ),
  waypoint_parents as (
    select a.parent_document_id as waypoint_id
    from waypoints w join guidebook.associations a
    on a.child_document_id = w.waypoint_id and a.parent_document_type = 'w'),
  waypoint_grandparents as (
    select a.parent_document_id as waypoint_id
    from waypoint_parents w join guidebook.associations a
    on a.child_document_id = w.waypoint_id and a.parent_document_type = 'w'),
  v as (
    select waypoint_id
    from waypoint_parents
    union select waypoint_id from waypoint_grandparents)
  update guidebook.cache_versions cv SET version = version + 1
  from v
  where cv.document_id = v.waypoint_id;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_of_waypoints(p_waypoints_ids integer[]) OWNER TO "www-data";

--
-- Name: update_cache_version_time(); Type: FUNCTION; Schema: guidebook; Owner: www-data
--

CREATE FUNCTION update_cache_version_time() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.last_updated = now();
    RETURN NEW;
END;
$$;


ALTER FUNCTION guidebook.update_cache_version_time() OWNER TO "www-data";

SET search_path = users, pg_catalog;

--
-- Name: check_forum_username(text); Type: FUNCTION; Schema: users; Owner: www-data
--

CREATE FUNCTION check_forum_username(name text) RETURNS boolean
    LANGUAGE plpgsql
    AS $_$
BEGIN
  IF name = NULL THEN
    RETURN FALSE;
  END IF;

  IF char_length(name) < 3 THEN
    RETURN FALSE;
  END IF;

  IF char_length(name) > 25 THEN
    RETURN FALSE;
  END IF;

  if name ~ '[^\w.-]' THEN
    RETURN FALSE;
  END IF;

  if left(name, 1) ~ '\W' THEN
    RETURN FALSE;
  END IF;

  if right(name, 1) ~ '[^A-Za-z0-9]' THEN
    RETURN FALSE;
  END IF;

  if name ~ '[-_\.]{2,}' THEN
    RETURN FALSE;
  END IF;

  if name ~
  '\.(js|json|css|htm|html|xml|jpg|jpeg|png|gif|bmp|ico|tif|tiff|woff)$'
  THEN
    RETURN FALSE;
  END IF;

  RETURN TRUE;
END;
$_$;


ALTER FUNCTION users.check_forum_username(name text) OWNER TO "www-data";

--
-- Name: update_mailinglists_email(); Type: FUNCTION; Schema: users; Owner: www-data
--

CREATE FUNCTION update_mailinglists_email() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE sympa.subscriber_table
  SET user_subscriber = NEW.email
  WHERE user_subscriber = OLD.email;
  RETURN null;
END;
$$;


ALTER FUNCTION users.update_mailinglists_email() OWNER TO "www-data";

SET search_path = alembic, pg_catalog;

SET default_tablespace = '';

--
-- Name: alembic_version; Type: TABLE; Schema: alembic; Owner: www-data
--

CREATE TABLE alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE alembic.alembic_version OWNER TO "www-data";

SET search_path = guidebook, pg_catalog;

--
-- Name: area_associations; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE area_associations (
    document_id integer NOT NULL,
    area_id integer NOT NULL
);


ALTER TABLE guidebook.area_associations OWNER TO "www-data";

--
-- Name: areas; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE areas (
    area_type area_type,
    document_id integer NOT NULL
);


ALTER TABLE guidebook.areas OWNER TO "www-data";

--
-- Name: areas_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE areas_archives (
    area_type area_type,
    id integer NOT NULL
);


ALTER TABLE guidebook.areas_archives OWNER TO "www-data";

--
-- Name: articles; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE articles (
    categories article_category[],
    activities activity_type[],
    article_type article_type,
    document_id integer NOT NULL
);


ALTER TABLE guidebook.articles OWNER TO "www-data";

--
-- Name: articles_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE articles_archives (
    categories article_category[],
    activities activity_type[],
    article_type article_type,
    id integer NOT NULL
);


ALTER TABLE guidebook.articles_archives OWNER TO "www-data";

--
-- Name: association_log; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE association_log (
    id integer NOT NULL,
    parent_document_id integer NOT NULL,
    parent_document_type character varying(1) NOT NULL,
    child_document_id integer NOT NULL,
    child_document_type character varying(1) NOT NULL,
    user_id integer NOT NULL,
    is_creation boolean NOT NULL,
    written_at timestamp with time zone NOT NULL
);


ALTER TABLE guidebook.association_log OWNER TO "www-data";

--
-- Name: association_log_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE association_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.association_log_id_seq OWNER TO "www-data";

--
-- Name: association_log_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE association_log_id_seq OWNED BY association_log.id;


--
-- Name: associations; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE associations (
    parent_document_id integer NOT NULL,
    parent_document_type character varying(1) NOT NULL,
    child_document_id integer NOT NULL,
    child_document_type character varying(1) NOT NULL
);


ALTER TABLE guidebook.associations OWNER TO "www-data";

--
-- Name: books; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE books (
    author character varying(100),
    editor character varying(100),
    activities activity_type[],
    url character varying(255),
    isbn character varying(17),
    book_types book_type[],
    nb_pages smallint,
    publication_date character varying(100),
    langs character varying(2)[],
    document_id integer NOT NULL
);


ALTER TABLE guidebook.books OWNER TO "www-data";

--
-- Name: books_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE books_archives (
    author character varying(100),
    editor character varying(100),
    activities activity_type[],
    url character varying(255),
    isbn character varying(17),
    book_types book_type[],
    nb_pages smallint,
    publication_date character varying(100),
    langs character varying(2)[],
    id integer NOT NULL
);


ALTER TABLE guidebook.books_archives OWNER TO "www-data";

--
-- Name: cache_versions; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE cache_versions (
    document_id integer NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    last_updated timestamp with time zone DEFAULT '2016-12-05 17:10:17.97437+00'::timestamp with time zone NOT NULL
);


ALTER TABLE guidebook.cache_versions OWNER TO "www-data";

--
-- Name: documents; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents (
    version integer DEFAULT 1 NOT NULL,
    protected boolean DEFAULT false NOT NULL,
    quality quality_type DEFAULT 'draft'::quality_type NOT NULL,
    type character varying(1),
    document_id integer NOT NULL,
    redirects_to integer
);


ALTER TABLE guidebook.documents OWNER TO "www-data";

--
-- Name: documents_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_archives (
    version integer DEFAULT 1 NOT NULL,
    protected boolean DEFAULT false NOT NULL,
    quality quality_type DEFAULT 'draft'::quality_type NOT NULL,
    type character varying(1),
    id integer NOT NULL,
    redirects_to integer,
    document_id integer NOT NULL
);


ALTER TABLE guidebook.documents_archives OWNER TO "www-data";

--
-- Name: documents_archives_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_archives_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_archives_id_seq OWNER TO "www-data";

--
-- Name: documents_archives_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_archives_id_seq OWNED BY documents_archives.id;


--
-- Name: documents_document_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_document_id_seq OWNER TO "www-data";

--
-- Name: documents_document_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_document_id_seq OWNED BY documents.document_id;


--
-- Name: documents_geometries; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_geometries (
    version integer NOT NULL,
    document_id integer NOT NULL,
    geom public.geometry(Point,3857),
    geom_detail public.geometry,
    CONSTRAINT enforce_srid_geom_detail CHECK ((public.st_srid(geom_detail) = 3857))
);


ALTER TABLE guidebook.documents_geometries OWNER TO "www-data";

--
-- Name: documents_geometries_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_geometries_archives (
    version integer NOT NULL,
    id integer NOT NULL,
    document_id integer NOT NULL,
    geom public.geometry(Point,3857),
    geom_detail public.geometry,
    CONSTRAINT enforce_srid_geom_detail CHECK ((public.st_srid(geom_detail) = 3857))
);


ALTER TABLE guidebook.documents_geometries_archives OWNER TO "www-data";

--
-- Name: documents_geometries_archives_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_geometries_archives_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_geometries_archives_id_seq OWNER TO "www-data";

--
-- Name: documents_geometries_archives_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_geometries_archives_id_seq OWNED BY documents_geometries_archives.id;


--
-- Name: documents_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_locales (
    id integer NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    title character varying(150) NOT NULL,
    summary character varying,
    description character varying,
    type character varying(1),
    document_id integer NOT NULL,
    lang character varying(2) NOT NULL
);


ALTER TABLE guidebook.documents_locales OWNER TO "www-data";

--
-- Name: documents_locales_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_locales_archives (
    id integer NOT NULL,
    version integer DEFAULT 1 NOT NULL,
    title character varying(150) NOT NULL,
    summary character varying,
    description character varying,
    type character varying(1),
    document_id integer NOT NULL,
    lang character varying(2) NOT NULL
);


ALTER TABLE guidebook.documents_locales_archives OWNER TO "www-data";

--
-- Name: documents_locales_archives_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_locales_archives_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_locales_archives_id_seq OWNER TO "www-data";

--
-- Name: documents_locales_archives_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_locales_archives_id_seq OWNED BY documents_locales_archives.id;


--
-- Name: documents_locales_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_locales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_locales_id_seq OWNER TO "www-data";

--
-- Name: documents_locales_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_locales_id_seq OWNED BY documents_locales.id;


--
-- Name: documents_tags; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_tags (
    user_id integer NOT NULL,
    document_id integer NOT NULL,
    document_type character varying(1) NOT NULL
);


ALTER TABLE guidebook.documents_tags OWNER TO "www-data";

--
-- Name: documents_tags_log; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_tags_log (
    id integer NOT NULL,
    user_id integer NOT NULL,
    document_id integer NOT NULL,
    document_type character varying(1) NOT NULL,
    is_creation boolean NOT NULL,
    written_at timestamp with time zone NOT NULL
);


ALTER TABLE guidebook.documents_tags_log OWNER TO "www-data";

--
-- Name: documents_tags_log_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_tags_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_tags_log_id_seq OWNER TO "www-data";

--
-- Name: documents_tags_log_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_tags_log_id_seq OWNED BY documents_tags_log.id;


--
-- Name: documents_topics; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_topics (
    document_locale_id integer NOT NULL,
    topic_id integer NOT NULL
);


ALTER TABLE guidebook.documents_topics OWNER TO "www-data";

--
-- Name: documents_versions; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE documents_versions (
    id integer NOT NULL,
    document_id integer NOT NULL,
    lang character varying(2) NOT NULL,
    document_archive_id integer NOT NULL,
    document_locales_archive_id integer NOT NULL,
    document_geometry_archive_id integer,
    history_metadata_id integer NOT NULL,
    masked boolean DEFAULT false NOT NULL
);


ALTER TABLE guidebook.documents_versions OWNER TO "www-data";

--
-- Name: documents_versions_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE documents_versions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.documents_versions_id_seq OWNER TO "www-data";

--
-- Name: documents_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE documents_versions_id_seq OWNED BY documents_versions.id;


--
-- Name: es_deleted_documents; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE es_deleted_documents (
    document_id integer NOT NULL,
    type character varying(1),
    deleted_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE guidebook.es_deleted_documents OWNER TO "www-data";

--
-- Name: es_deleted_documents_document_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE es_deleted_documents_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.es_deleted_documents_document_id_seq OWNER TO "www-data";

--
-- Name: es_deleted_documents_document_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE es_deleted_documents_document_id_seq OWNED BY es_deleted_documents.document_id;


--
-- Name: es_deleted_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE es_deleted_locales (
    document_id integer NOT NULL,
    type character varying(1),
    lang character varying(2) NOT NULL,
    deleted_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE guidebook.es_deleted_locales OWNER TO "www-data";

--
-- Name: es_deleted_locales_document_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE es_deleted_locales_document_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.es_deleted_locales_document_id_seq OWNER TO "www-data";

--
-- Name: es_deleted_locales_document_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE es_deleted_locales_document_id_seq OWNED BY es_deleted_locales.document_id;


--
-- Name: es_sync_status; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE es_sync_status (
    last_update timestamp with time zone,
    id integer NOT NULL,
    CONSTRAINT one_row_constraint CHECK ((id = 1))
);


ALTER TABLE guidebook.es_sync_status OWNER TO "www-data";

--
-- Name: es_sync_status_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE es_sync_status_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.es_sync_status_id_seq OWNER TO "www-data";

--
-- Name: es_sync_status_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE es_sync_status_id_seq OWNED BY es_sync_status.id;


--
-- Name: feed_document_changes; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE feed_document_changes (
    change_id integer NOT NULL,
    "time" timestamp with time zone NOT NULL,
    user_id integer NOT NULL,
    change_type feed_change_type NOT NULL,
    document_id integer NOT NULL,
    document_type character varying(1) NOT NULL,
    activities activity_type[] DEFAULT '{}'::activity_type[] NOT NULL,
    area_ids integer[] DEFAULT '{}'::integer[] NOT NULL,
    user_ids integer[] DEFAULT '{}'::integer[] NOT NULL,
    image1_id integer,
    image2_id integer,
    image3_id integer,
    more_images boolean DEFAULT false NOT NULL,
    langs lang[] DEFAULT '{}'::lang[] NOT NULL
);


ALTER TABLE guidebook.feed_document_changes OWNER TO "www-data";

--
-- Name: feed_document_changes_change_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE feed_document_changes_change_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.feed_document_changes_change_id_seq OWNER TO "www-data";

--
-- Name: feed_document_changes_change_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE feed_document_changes_change_id_seq OWNED BY feed_document_changes.change_id;


--
-- Name: feed_filter_area; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE feed_filter_area (
    area_id integer NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE guidebook.feed_filter_area OWNER TO "www-data";

--
-- Name: feed_followed_users; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE feed_followed_users (
    followed_user_id integer NOT NULL,
    follower_user_id integer NOT NULL,
    CONSTRAINT check_feed_followed_user_self_follow CHECK ((followed_user_id <> follower_user_id))
);


ALTER TABLE guidebook.feed_followed_users OWNER TO "www-data";

--
-- Name: history_metadata; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE history_metadata (
    id integer NOT NULL,
    user_id integer NOT NULL,
    comment character varying(200),
    written_at timestamp with time zone NOT NULL
);


ALTER TABLE guidebook.history_metadata OWNER TO "www-data";

--
-- Name: history_metadata_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE history_metadata_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.history_metadata_id_seq OWNER TO "www-data";

--
-- Name: history_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE history_metadata_id_seq OWNED BY history_metadata.id;


--
-- Name: images; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE images (
    activities activity_type[],
    categories image_category[],
    image_type image_type,
    author character varying(100),
    elevation smallint,
    height smallint,
    width smallint,
    file_size integer,
    filename character varying(30) NOT NULL,
    date_time timestamp with time zone,
    camera_name character varying(100),
    exposure_time double precision,
    focal_length double precision,
    fnumber double precision,
    iso_speed smallint,
    document_id integer NOT NULL
);


ALTER TABLE guidebook.images OWNER TO "www-data";

--
-- Name: images_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE images_archives (
    activities activity_type[],
    categories image_category[],
    image_type image_type,
    author character varying(100),
    elevation smallint,
    height smallint,
    width smallint,
    file_size integer,
    filename character varying(30) NOT NULL,
    date_time timestamp with time zone,
    camera_name character varying(100),
    exposure_time double precision,
    focal_length double precision,
    fnumber double precision,
    iso_speed smallint,
    id integer NOT NULL
);


ALTER TABLE guidebook.images_archives OWNER TO "www-data";

--
-- Name: langs; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE langs (
    lang character varying(2) NOT NULL
);


ALTER TABLE guidebook.langs OWNER TO "www-data";

--
-- Name: map_associations; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE map_associations (
    document_id integer NOT NULL,
    topo_map_id integer NOT NULL
);


ALTER TABLE guidebook.map_associations OWNER TO "www-data";

--
-- Name: maps; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE maps (
    editor map_editor,
    scale map_scale,
    code character varying,
    document_id integer NOT NULL
);


ALTER TABLE guidebook.maps OWNER TO "www-data";

--
-- Name: maps_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE maps_archives (
    editor map_editor,
    scale map_scale,
    code character varying,
    id integer NOT NULL
);


ALTER TABLE guidebook.maps_archives OWNER TO "www-data";

--
-- Name: outings; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE outings (
    activities activity_type[] NOT NULL,
    date_start date NOT NULL,
    date_end date NOT NULL,
    frequentation frequentation_type,
    participant_count smallint,
    elevation_min smallint,
    elevation_max smallint,
    elevation_access smallint,
    elevation_up_snow smallint,
    elevation_down_snow smallint,
    height_diff_up smallint,
    height_diff_down smallint,
    length_total integer,
    partial_trip boolean,
    public_transport boolean,
    access_condition access_condition,
    lift_status lift_status,
    condition_rating condition_rating,
    snow_quantity condition_rating,
    snow_quality condition_rating,
    glacier_rating glacier_rating,
    avalanche_signs avalanche_signs[],
    hut_status hut_status,
    document_id integer NOT NULL,
    disable_comments boolean,
    height_diff_difficulties smallint,
    ski_rating ski_rating,
    labande_global_rating global_rating,
    global_rating global_rating,
    engagement_rating engagement_rating,
    equipment_rating equipment_rating,
    ice_rating ice_rating,
    rock_free_rating climbing_rating,
    via_ferrata_rating via_ferrata_rating,
    hiking_rating hiking_rating,
    snowshoe_rating snowshoe_rating,
    mtb_up_rating mtb_up_rating,
    mtb_down_rating mtb_down_rating
);


ALTER TABLE guidebook.outings OWNER TO "www-data";

--
-- Name: outings_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE outings_archives (
    activities activity_type[] NOT NULL,
    date_start date NOT NULL,
    date_end date NOT NULL,
    frequentation frequentation_type,
    participant_count smallint,
    elevation_min smallint,
    elevation_max smallint,
    elevation_access smallint,
    elevation_up_snow smallint,
    elevation_down_snow smallint,
    height_diff_up smallint,
    height_diff_down smallint,
    length_total integer,
    partial_trip boolean,
    public_transport boolean,
    access_condition access_condition,
    lift_status lift_status,
    condition_rating condition_rating,
    snow_quantity condition_rating,
    snow_quality condition_rating,
    glacier_rating glacier_rating,
    avalanche_signs avalanche_signs[],
    hut_status hut_status,
    id integer NOT NULL,
    disable_comments boolean,
    height_diff_difficulties smallint,
    ski_rating ski_rating,
    labande_global_rating global_rating,
    global_rating global_rating,
    engagement_rating engagement_rating,
    equipment_rating equipment_rating,
    ice_rating ice_rating,
    rock_free_rating climbing_rating,
    via_ferrata_rating via_ferrata_rating,
    hiking_rating hiking_rating,
    snowshoe_rating snowshoe_rating,
    mtb_up_rating mtb_up_rating,
    mtb_down_rating mtb_down_rating
);


ALTER TABLE guidebook.outings_archives OWNER TO "www-data";

--
-- Name: outings_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE outings_locales (
    participants character varying,
    access_comment character varying,
    weather character varying,
    timing character varying,
    conditions_levels character varying,
    conditions character varying,
    avalanches character varying,
    hut_comment character varying,
    route_description character varying,
    id integer NOT NULL
);


ALTER TABLE guidebook.outings_locales OWNER TO "www-data";

--
-- Name: outings_locales_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE outings_locales_archives (
    participants character varying,
    access_comment character varying,
    weather character varying,
    timing character varying,
    conditions_levels character varying,
    conditions character varying,
    avalanches character varying,
    hut_comment character varying,
    route_description character varying,
    id integer NOT NULL
);


ALTER TABLE guidebook.outings_locales_archives OWNER TO "www-data";

--
-- Name: routes; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE routes (
    activities activity_type[] NOT NULL,
    elevation_min smallint,
    elevation_max smallint,
    height_diff_up smallint,
    height_diff_down smallint,
    route_length integer,
    difficulties_height smallint,
    height_diff_access smallint,
    height_diff_difficulties smallint,
    route_types route_type[],
    orientations orientation_type[],
    durations route_duration_type[],
    glacier_gear glacier_gear_type DEFAULT 'no'::glacier_gear_type NOT NULL,
    configuration route_configuration_type[],
    lift_access boolean,
    ski_rating ski_rating,
    ski_exposition exposition_rating,
    labande_ski_rating labande_ski_rating,
    labande_global_rating global_rating,
    global_rating global_rating,
    engagement_rating engagement_rating,
    risk_rating risk_rating,
    equipment_rating equipment_rating,
    ice_rating ice_rating,
    mixed_rating mixed_rating,
    exposition_rock_rating exposition_rock_rating,
    rock_free_rating climbing_rating,
    rock_required_rating climbing_rating,
    aid_rating aid_rating,
    via_ferrata_rating via_ferrata_rating,
    hiking_rating hiking_rating,
    hiking_mtb_exposition exposition_rating,
    snowshoe_rating snowshoe_rating,
    mtb_up_rating mtb_up_rating,
    mtb_down_rating mtb_down_rating,
    mtb_length_asphalt integer,
    mtb_length_trail integer,
    mtb_height_diff_portages integer,
    rock_types rock_type[],
    climbing_outdoor_type climbing_outdoor_type,
    document_id integer NOT NULL,
    main_waypoint_id integer,
    slackline_type slackline_type,
    slackline_height smallint,
    public_transportation_rating public_transportation_ratings,
    calculated_duration double precision
);


ALTER TABLE guidebook.routes OWNER TO "www-data";

--
-- Name: routes_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE routes_archives (
    activities activity_type[] NOT NULL,
    elevation_min smallint,
    elevation_max smallint,
    height_diff_up smallint,
    height_diff_down smallint,
    route_length integer,
    difficulties_height smallint,
    height_diff_access smallint,
    height_diff_difficulties smallint,
    route_types route_type[],
    orientations orientation_type[],
    durations route_duration_type[],
    glacier_gear glacier_gear_type DEFAULT 'no'::glacier_gear_type NOT NULL,
    configuration route_configuration_type[],
    lift_access boolean,
    ski_rating ski_rating,
    ski_exposition exposition_rating,
    labande_ski_rating labande_ski_rating,
    labande_global_rating global_rating,
    global_rating global_rating,
    engagement_rating engagement_rating,
    risk_rating risk_rating,
    equipment_rating equipment_rating,
    ice_rating ice_rating,
    mixed_rating mixed_rating,
    exposition_rock_rating exposition_rock_rating,
    rock_free_rating climbing_rating,
    rock_required_rating climbing_rating,
    aid_rating aid_rating,
    via_ferrata_rating via_ferrata_rating,
    hiking_rating hiking_rating,
    hiking_mtb_exposition exposition_rating,
    snowshoe_rating snowshoe_rating,
    mtb_up_rating mtb_up_rating,
    mtb_down_rating mtb_down_rating,
    mtb_length_asphalt integer,
    mtb_length_trail integer,
    mtb_height_diff_portages integer,
    rock_types rock_type[],
    climbing_outdoor_type climbing_outdoor_type,
    id integer NOT NULL,
    main_waypoint_id integer,
    slackline_type slackline_type,
    slackline_height smallint,
    public_transportation_rating public_transportation_ratings,
    calculated_duration double precision
);


ALTER TABLE guidebook.routes_archives OWNER TO "www-data";

--
-- Name: routes_for_outings; Type: VIEW; Schema: guidebook; Owner: www-data
--

CREATE VIEW routes_for_outings AS
 SELECT associations.child_document_id AS outing_id,
    array_agg(associations.parent_document_id) AS route_ids
   FROM associations
  WHERE (((associations.parent_document_type)::text = 'r'::text) AND ((associations.child_document_type)::text = 'o'::text))
  GROUP BY associations.child_document_id;


ALTER VIEW guidebook.routes_for_outings OWNER TO "www-data";

--
-- Name: routes_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE routes_locales (
    slope character varying,
    remarks character varying,
    gear character varying,
    external_resources character varying,
    route_history character varying,
    id integer NOT NULL,
    title_prefix character varying,
    slackline_anchor1 character varying,
    slackline_anchor2 character varying
);


ALTER TABLE guidebook.routes_locales OWNER TO "www-data";

--
-- Name: routes_locales_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE routes_locales_archives (
    slope character varying,
    remarks character varying,
    gear character varying,
    external_resources character varying,
    route_history character varying,
    id integer NOT NULL,
    slackline_anchor1 character varying,
    slackline_anchor2 character varying
);


ALTER TABLE guidebook.routes_locales_archives OWNER TO "www-data";

--
-- Name: stopareas; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE stopareas (
    stoparea_id integer NOT NULL,
    navitia_id character varying NOT NULL,
    stoparea_name character varying NOT NULL,
    line character varying NOT NULL,
    operator character varying NOT NULL,
    geom public.geometry(Point,3857)
);


ALTER TABLE guidebook.stopareas OWNER TO "www-data";

--
-- Name: stopareas_stoparea_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE stopareas_stoparea_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.stopareas_stoparea_id_seq OWNER TO "www-data";

--
-- Name: stopareas_stoparea_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE stopareas_stoparea_id_seq OWNED BY stopareas.stoparea_id;


--
-- Name: user_profiles; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE user_profiles (
    activities activity_type[],
    categories user_category[],
    document_id integer NOT NULL
);


ALTER TABLE guidebook.user_profiles OWNER TO "www-data";

--
-- Name: user_profiles_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE user_profiles_archives (
    activities activity_type[],
    categories user_category[],
    id integer NOT NULL
);


ALTER TABLE guidebook.user_profiles_archives OWNER TO "www-data";

--
-- Name: users_for_outings; Type: VIEW; Schema: guidebook; Owner: www-data
--

CREATE VIEW users_for_outings AS
 SELECT associations.child_document_id AS outing_id,
    array_agg(associations.parent_document_id) AS user_ids
   FROM associations
  WHERE (((associations.parent_document_type)::text = 'u'::text) AND ((associations.child_document_type)::text = 'o'::text))
  GROUP BY associations.child_document_id;


ALTER VIEW guidebook.users_for_outings OWNER TO "www-data";

--
-- Name: users_for_routes; Type: VIEW; Schema: guidebook; Owner: www-data
--

CREATE VIEW users_for_routes AS
 SELECT documents_tags.document_id AS route_id,
    array_agg(documents_tags.user_id) AS user_ids
   FROM documents_tags
  GROUP BY documents_tags.document_id;


ALTER VIEW guidebook.users_for_routes OWNER TO "www-data";

--
-- Name: waypoints; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE waypoints (
    waypoint_type waypoint_type NOT NULL,
    elevation smallint,
    elevation_min smallint,
    prominence smallint,
    height_max smallint,
    height_median smallint,
    height_min smallint,
    routes_quantity smallint,
    climbing_outdoor_types climbing_outdoor_type[],
    climbing_indoor_types climbing_indoor_type[],
    climbing_rating_max climbing_rating,
    climbing_rating_min climbing_rating,
    climbing_rating_median climbing_rating,
    equipment_ratings equipment_rating[],
    climbing_styles climbing_style[],
    children_proof children_proof_type,
    rain_proof rain_proof_type,
    orientations orientation_type[],
    best_periods month_type[],
    product_types product_type[],
    length smallint,
    slope smallint,
    ground_types ground_type[],
    paragliding_rating paragliding_rating,
    exposition_rating exposition_rating,
    rock_types rock_type[],
    weather_station_types weather_station_type[],
    url character varying(255),
    maps_info character varying(300),
    phone character varying(50),
    public_transportation_rating public_transportation_ratings,
    snow_clearance_rating snow_clearance_rating,
    lift_access boolean,
    parking_fee parking_fee_type,
    phone_custodian character varying(50),
    custodianship custodianship_type,
    matress_unstaffed boolean,
    blanket_unstaffed boolean,
    gas_unstaffed boolean,
    heating_unstaffed boolean,
    access_time access_time_type,
    capacity smallint,
    capacity_staffed smallint,
    document_id integer NOT NULL,
    slackline_types slackline_type[],
    slackline_length_min smallint,
    slackline_length_max smallint,
    public_transportation_types public_transportation_type[]
);


ALTER TABLE guidebook.waypoints OWNER TO "www-data";

--
-- Name: waypoints_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE waypoints_archives (
    waypoint_type waypoint_type NOT NULL,
    elevation smallint,
    elevation_min smallint,
    prominence smallint,
    height_max smallint,
    height_median smallint,
    height_min smallint,
    routes_quantity smallint,
    climbing_outdoor_types climbing_outdoor_type[],
    climbing_indoor_types climbing_indoor_type[],
    climbing_rating_max climbing_rating,
    climbing_rating_min climbing_rating,
    climbing_rating_median climbing_rating,
    equipment_ratings equipment_rating[],
    climbing_styles climbing_style[],
    children_proof children_proof_type,
    rain_proof rain_proof_type,
    orientations orientation_type[],
    best_periods month_type[],
    product_types product_type[],
    length smallint,
    slope smallint,
    ground_types ground_type[],
    paragliding_rating paragliding_rating,
    exposition_rating exposition_rating,
    rock_types rock_type[],
    weather_station_types weather_station_type[],
    url character varying(255),
    maps_info character varying(300),
    phone character varying(50),
    public_transportation_rating public_transportation_ratings,
    snow_clearance_rating snow_clearance_rating,
    lift_access boolean,
    parking_fee parking_fee_type,
    phone_custodian character varying(50),
    custodianship custodianship_type,
    matress_unstaffed boolean,
    blanket_unstaffed boolean,
    gas_unstaffed boolean,
    heating_unstaffed boolean,
    access_time access_time_type,
    capacity smallint,
    capacity_staffed smallint,
    id integer NOT NULL,
    slackline_types slackline_type[],
    slackline_length_min smallint,
    slackline_length_max smallint,
    public_transportation_types public_transportation_type[]
);


ALTER TABLE guidebook.waypoints_archives OWNER TO "www-data";

--
-- Name: waypoints_for_outings; Type: VIEW; Schema: guidebook; Owner: www-data
--

CREATE VIEW waypoints_for_outings AS
 WITH linked_waypoints AS (
         SELECT associations.child_document_id AS route_id,
            associations.parent_document_id AS waypoint_id
           FROM associations
          WHERE (((associations.parent_document_type)::text = 'w'::text) AND ((associations.child_document_type)::text = 'r'::text))
        ), waypoint_parents AS (
         SELECT linked_waypoints.route_id,
            associations.parent_document_id AS waypoint_id
           FROM (linked_waypoints
             JOIN associations ON (((associations.child_document_id = linked_waypoints.waypoint_id) AND ((associations.parent_document_type)::text = 'w'::text))))
        ), waypoint_grandparents AS (
         SELECT waypoint_parents.route_id,
            associations.parent_document_id AS waypoint_id
           FROM (waypoint_parents
             JOIN associations ON (((associations.child_document_id = waypoint_parents.waypoint_id) AND ((associations.parent_document_type)::text = 'w'::text))))
        ), all_waypoints AS (
         SELECT linked_waypoints.route_id,
            linked_waypoints.waypoint_id
           FROM linked_waypoints
        UNION
         SELECT waypoint_parents.route_id,
            waypoint_parents.waypoint_id
           FROM waypoint_parents
        UNION
         SELECT waypoint_grandparents.route_id,
            waypoint_grandparents.waypoint_id
           FROM waypoint_grandparents
        ), waypoints_for_outings AS (
         SELECT associations.child_document_id AS outing_id,
            all_waypoints.waypoint_id
           FROM (associations
             JOIN all_waypoints ON (((associations.parent_document_id = all_waypoints.route_id) AND ((associations.parent_document_type)::text = 'r'::text) AND ((associations.child_document_type)::text = 'o'::text))))
        )
 SELECT waypoints_for_outings.outing_id,
    array_agg(waypoints_for_outings.waypoint_id) AS waypoint_ids
   FROM waypoints_for_outings
  GROUP BY waypoints_for_outings.outing_id;


ALTER VIEW guidebook.waypoints_for_outings OWNER TO "www-data";

--
-- Name: waypoints_for_routes; Type: VIEW; Schema: guidebook; Owner: www-data
--

CREATE VIEW waypoints_for_routes AS
 WITH linked_waypoints AS (
         SELECT associations.child_document_id AS route_id,
            associations.parent_document_id AS waypoint_id
           FROM associations
          WHERE (((associations.parent_document_type)::text = 'w'::text) AND ((associations.child_document_type)::text = 'r'::text))
        ), waypoint_parents AS (
         SELECT linked_waypoints.route_id,
            associations.parent_document_id AS waypoint_id
           FROM (linked_waypoints
             JOIN associations ON (((associations.child_document_id = linked_waypoints.waypoint_id) AND ((associations.parent_document_type)::text = 'w'::text))))
        ), waypoint_grandparents AS (
         SELECT waypoint_parents.route_id,
            associations.parent_document_id AS waypoint_id
           FROM (waypoint_parents
             JOIN associations ON (((associations.child_document_id = waypoint_parents.waypoint_id) AND ((associations.parent_document_type)::text = 'w'::text))))
        ), all_waypoints AS (
         SELECT linked_waypoints.route_id,
            linked_waypoints.waypoint_id
           FROM linked_waypoints
        UNION
         SELECT waypoint_parents.route_id,
            waypoint_parents.waypoint_id
           FROM waypoint_parents
        UNION
         SELECT waypoint_grandparents.route_id,
            waypoint_grandparents.waypoint_id
           FROM waypoint_grandparents
        )
 SELECT all_waypoints.route_id,
    array_agg(all_waypoints.waypoint_id) AS waypoint_ids
   FROM all_waypoints
  GROUP BY all_waypoints.route_id;


ALTER VIEW guidebook.waypoints_for_routes OWNER TO "www-data";

--
-- Name: waypoints_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE waypoints_locales (
    access character varying,
    access_period character varying,
    id integer NOT NULL,
    external_resources character varying
);


ALTER TABLE guidebook.waypoints_locales OWNER TO "www-data";

--
-- Name: waypoints_locales_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE waypoints_locales_archives (
    access character varying,
    access_period character varying,
    id integer NOT NULL,
    external_resources character varying
);


ALTER TABLE guidebook.waypoints_locales_archives OWNER TO "www-data";

--
-- Name: waypoints_stopareas; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE waypoints_stopareas (
    waypoint_stoparea_id integer NOT NULL,
    stoparea_id integer NOT NULL,
    waypoint_id integer NOT NULL,
    distance double precision NOT NULL
);


ALTER TABLE guidebook.waypoints_stopareas OWNER TO "www-data";

--
-- Name: waypoints_stopareas_waypoint_stoparea_id_seq; Type: SEQUENCE; Schema: guidebook; Owner: www-data
--

CREATE SEQUENCE waypoints_stopareas_waypoint_stoparea_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE guidebook.waypoints_stopareas_waypoint_stoparea_id_seq OWNER TO "www-data";

--
-- Name: waypoints_stopareas_waypoint_stoparea_id_seq; Type: SEQUENCE OWNED BY; Schema: guidebook; Owner: www-data
--

ALTER SEQUENCE waypoints_stopareas_waypoint_stoparea_id_seq OWNED BY waypoints_stopareas.waypoint_stoparea_id;


--
-- Name: xreports; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE xreports (
    elevation smallint,
    date date,
    nb_participants smallint,
    nb_impacted smallint,
    rescue boolean,
    avalanche_level avalanche_level,
    severity severity,
    author_status author_status,
    age smallint,
    gender gender,
    previous_injuries previous_injuries,
    document_id integer NOT NULL,
    avalanche_slope avalanche_slope,
    disable_comments boolean,
    anonymous boolean,
    event_activity event_activity_type NOT NULL,
    event_type event_type,
    autonomy autonomy,
    activity_rate activity_rate,
    supervision supervision_type,
    qualification qualification_type
);


ALTER TABLE guidebook.xreports OWNER TO "www-data";

--
-- Name: xreports_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE xreports_archives (
    elevation smallint,
    date date,
    nb_participants smallint,
    nb_impacted smallint,
    rescue boolean,
    avalanche_level avalanche_level,
    severity severity,
    author_status author_status,
    age smallint,
    gender gender,
    previous_injuries previous_injuries,
    id integer NOT NULL,
    avalanche_slope avalanche_slope,
    disable_comments boolean,
    anonymous boolean,
    event_activity event_activity_type NOT NULL,
    event_type event_type,
    autonomy autonomy,
    activity_rate activity_rate,
    supervision supervision_type,
    qualification qualification_type
);


ALTER TABLE guidebook.xreports_archives OWNER TO "www-data";

--
-- Name: xreports_locales; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE xreports_locales (
    place character varying,
    route_study character varying,
    conditions character varying,
    training character varying,
    motivations character varying,
    group_management character varying,
    risk character varying,
    time_management character varying,
    safety character varying,
    reduce_impact character varying,
    increase_impact character varying,
    modifications character varying,
    other_comments character varying,
    id integer NOT NULL
);


ALTER TABLE guidebook.xreports_locales OWNER TO "www-data";

--
-- Name: xreports_locales_archives; Type: TABLE; Schema: guidebook; Owner: www-data
--

CREATE TABLE xreports_locales_archives (
    place character varying,
    route_study character varying,
    conditions character varying,
    training character varying,
    motivations character varying,
    group_management character varying,
    risk character varying,
    time_management character varying,
    safety character varying,
    reduce_impact character varying,
    increase_impact character varying,
    modifications character varying,
    other_comments character varying,
    id integer NOT NULL
);


ALTER TABLE guidebook.xreports_locales_archives OWNER TO "www-data";

SET search_path = sympa, pg_catalog;

--
-- Name: subscriber_table; Type: TABLE; Schema: sympa; Owner: www-data
--

CREATE TABLE subscriber_table (
    list_subscriber character varying(50) NOT NULL,
    user_subscriber character varying(200) NOT NULL,
    user_id integer NOT NULL,
    date_subscriber timestamp without time zone DEFAULT now() NOT NULL,
    update_subscriber timestamp without time zone,
    visibility_subscriber character varying(20),
    reception_subscriber character varying(20),
    bounce_subscriber character varying(35),
    bounce_score_subscriber integer,
    comment_subscriber character varying(150),
    subscribed_subscriber integer,
    included_subscriber integer,
    include_sources_subscriber character varying(50)
);


ALTER TABLE sympa.subscriber_table OWNER TO "www-data";

SET search_path = tracking, pg_catalog;

--
-- Name: activities; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE activities (
    id integer NOT NULL,
    user_id integer NOT NULL,
    vendor character varying(255) NOT NULL,
    vendor_id character varying(255) NOT NULL,
    name character varying(255),
    type character varying(255) NOT NULL,
    date character varying(255) NOT NULL,
    geojson json,
    length integer,
    duration integer,
    height_diff_up integer,
    miniature character varying(28)
);


ALTER TABLE tracking.activities OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE activities_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tracking.activities_id_seq OWNER TO postgres;

--
-- Name: activities_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE activities_id_seq OWNED BY activities.id;


--
-- Name: migrations; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE migrations (
    id integer NOT NULL,
    name character varying(255),
    batch integer,
    migration_time timestamp with time zone
);


ALTER TABLE tracking.migrations OWNER TO postgres;

--
-- Name: migrations_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tracking.migrations_id_seq OWNER TO postgres;

--
-- Name: migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE migrations_id_seq OWNED BY migrations.id;


--
-- Name: migrations_lock; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE migrations_lock (
    index integer NOT NULL,
    is_locked integer
);


ALTER TABLE tracking.migrations_lock OWNER TO postgres;

--
-- Name: migrations_lock_index_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE migrations_lock_index_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tracking.migrations_lock_index_seq OWNER TO postgres;

--
-- Name: migrations_lock_index_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE migrations_lock_index_seq OWNED BY migrations_lock.index;


--
-- Name: polar; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE polar (
    id integer NOT NULL,
    webhook_secret character varying(256) NOT NULL
);


ALTER TABLE tracking.polar OWNER TO postgres;

--
-- Name: polar_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE polar_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tracking.polar_id_seq OWNER TO postgres;

--
-- Name: polar_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE polar_id_seq OWNED BY polar.id;


--
-- Name: strava; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE strava (
    id integer NOT NULL,
    subscription_id integer NOT NULL
);


ALTER TABLE tracking.strava OWNER TO postgres;

--
-- Name: strava_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE strava_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE tracking.strava_id_seq OWNER TO postgres;

--
-- Name: strava_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE strava_id_seq OWNED BY strava.id;


--
-- Name: users; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE users (
    c2c_id integer NOT NULL,
    strava_id integer,
    strava_access_token character varying(4096),
    strava_expires_at timestamp with time zone,
    strava_refresh_token character varying(4096),
    suunto_username character varying(255),
    suunto_access_token character varying(4096),
    suunto_expires_at timestamp with time zone,
    suunto_refresh_token character varying(4096),
    garmin_token character varying(255),
    garmin_token_secret character varying(255),
    decathlon_id character varying(255),
    decathlon_access_token character varying(4096),
    decathlon_expires_at timestamp with time zone,
    decathlon_refresh_token character varying(4096),
    decathlon_webhook_id character varying(255),
    polar_id bigint,
    polar_token character varying(256),
    coros_id character varying(256),
    coros_access_token character varying(256),
    coros_expires_at timestamp with time zone,
    coros_refresh_token character varying(256)
);


ALTER TABLE tracking.users OWNER TO postgres;

SET search_path = users, pg_catalog;

--
-- Name: sso_external_id; Type: TABLE; Schema: users; Owner: www-data
--

CREATE TABLE sso_external_id (
    domain character varying NOT NULL,
    external_id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying,
    expire timestamp with time zone
);


ALTER TABLE users.sso_external_id OWNER TO "www-data";

--
-- Name: sso_key; Type: TABLE; Schema: users; Owner: www-data
--

CREATE TABLE sso_key (
    domain character varying NOT NULL,
    key character varying NOT NULL
);


ALTER TABLE users.sso_key OWNER TO "www-data";

--
-- Name: token; Type: TABLE; Schema: users; Owner: www-data
--

CREATE TABLE token (
    value character varying NOT NULL,
    expire timestamp with time zone NOT NULL,
    userid integer NOT NULL
);


ALTER TABLE users.token OWNER TO "www-data";

--
-- Name: user; Type: TABLE; Schema: users; Owner: www-data
--

CREATE TABLE "user" (
    id integer NOT NULL,
    username character varying(200) NOT NULL,
    name character varying(200) NOT NULL,
    forum_username character varying(25) NOT NULL,
    email character varying(200) NOT NULL,
    email_validated boolean NOT NULL,
    email_to_validate character varying(200),
    moderator boolean NOT NULL,
    validation_nonce character varying(200),
    validation_nonce_expire timestamp with time zone,
    password character varying(255) NOT NULL,
    last_modified timestamp with time zone NOT NULL,
    lang character varying(2) NOT NULL,
    is_profile_public boolean DEFAULT false NOT NULL,
    feed_filter_activities guidebook.activity_type[] DEFAULT '{}'::guidebook.activity_type[] NOT NULL,
    feed_followed_only boolean DEFAULT false NOT NULL,
    blocked boolean DEFAULT false NOT NULL,
    feed_filter_langs guidebook.lang[] DEFAULT '{}'::guidebook.lang[] NOT NULL,
    ratelimit_remaining integer,
    ratelimit_reset timestamp with time zone,
    ratelimit_last_blocked_window timestamp with time zone,
    ratelimit_times integer DEFAULT 0 NOT NULL,
    robot boolean DEFAULT false NOT NULL,
    tos_validated timestamp with time zone,
    CONSTRAINT forum_username_check_constraint CHECK (check_forum_username((forum_username)::text))
);


ALTER TABLE users."user" OWNER TO "www-data";

SET search_path = guidebook, pg_catalog;

--
-- Name: association_log id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY association_log ALTER COLUMN id SET DEFAULT nextval('association_log_id_seq'::regclass);


--
-- Name: documents document_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents ALTER COLUMN document_id SET DEFAULT nextval('documents_document_id_seq'::regclass);


--
-- Name: documents_archives id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_archives ALTER COLUMN id SET DEFAULT nextval('documents_archives_id_seq'::regclass);


--
-- Name: documents_geometries_archives id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries_archives ALTER COLUMN id SET DEFAULT nextval('documents_geometries_archives_id_seq'::regclass);


--
-- Name: documents_locales id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales ALTER COLUMN id SET DEFAULT nextval('documents_locales_id_seq'::regclass);


--
-- Name: documents_locales_archives id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales_archives ALTER COLUMN id SET DEFAULT nextval('documents_locales_archives_id_seq'::regclass);


--
-- Name: documents_tags_log id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags_log ALTER COLUMN id SET DEFAULT nextval('documents_tags_log_id_seq'::regclass);


--
-- Name: documents_versions id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions ALTER COLUMN id SET DEFAULT nextval('documents_versions_id_seq'::regclass);


--
-- Name: es_deleted_documents document_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_deleted_documents ALTER COLUMN document_id SET DEFAULT nextval('es_deleted_documents_document_id_seq'::regclass);


--
-- Name: es_deleted_locales document_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_deleted_locales ALTER COLUMN document_id SET DEFAULT nextval('es_deleted_locales_document_id_seq'::regclass);


--
-- Name: es_sync_status id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_sync_status ALTER COLUMN id SET DEFAULT nextval('es_sync_status_id_seq'::regclass);


--
-- Name: feed_document_changes change_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes ALTER COLUMN change_id SET DEFAULT nextval('feed_document_changes_change_id_seq'::regclass);


--
-- Name: history_metadata id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY history_metadata ALTER COLUMN id SET DEFAULT nextval('history_metadata_id_seq'::regclass);


--
-- Name: stopareas stoparea_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY stopareas ALTER COLUMN stoparea_id SET DEFAULT nextval('stopareas_stoparea_id_seq'::regclass);


--
-- Name: waypoints_stopareas waypoint_stoparea_id; Type: DEFAULT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_stopareas ALTER COLUMN waypoint_stoparea_id SET DEFAULT nextval('waypoints_stopareas_waypoint_stoparea_id_seq'::regclass);


SET search_path = tracking, pg_catalog;

--
-- Name: activities id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY activities ALTER COLUMN id SET DEFAULT nextval('activities_id_seq'::regclass);


--
-- Name: migrations id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY migrations ALTER COLUMN id SET DEFAULT nextval('migrations_id_seq'::regclass);


--
-- Name: migrations_lock index; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY migrations_lock ALTER COLUMN index SET DEFAULT nextval('migrations_lock_index_seq'::regclass);


--
-- Name: polar id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY polar ALTER COLUMN id SET DEFAULT nextval('polar_id_seq'::regclass);


--
-- Name: strava id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY strava ALTER COLUMN id SET DEFAULT nextval('strava_id_seq'::regclass);


SET search_path = guidebook, pg_catalog;

--
-- Name: area_associations area_associations_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY area_associations
    ADD CONSTRAINT area_associations_pkey PRIMARY KEY (document_id, area_id);


--
-- Name: areas_archives areas_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY areas_archives
    ADD CONSTRAINT areas_archives_pkey PRIMARY KEY (id);


--
-- Name: areas areas_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY areas
    ADD CONSTRAINT areas_pkey PRIMARY KEY (document_id);


--
-- Name: articles_archives articles_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY articles_archives
    ADD CONSTRAINT articles_archives_pkey PRIMARY KEY (id);


--
-- Name: articles articles_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY articles
    ADD CONSTRAINT articles_pkey PRIMARY KEY (document_id);


--
-- Name: association_log association_log_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY association_log
    ADD CONSTRAINT association_log_pkey PRIMARY KEY (id);


--
-- Name: associations associations_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY associations
    ADD CONSTRAINT associations_pkey PRIMARY KEY (parent_document_id, child_document_id);


--
-- Name: books_archives books_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY books_archives
    ADD CONSTRAINT books_archives_pkey PRIMARY KEY (id);


--
-- Name: books books_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY books
    ADD CONSTRAINT books_pkey PRIMARY KEY (document_id);


--
-- Name: cache_versions cache_versions_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY cache_versions
    ADD CONSTRAINT cache_versions_pkey PRIMARY KEY (document_id);


--
-- Name: documents_archives documents_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_archives
    ADD CONSTRAINT documents_archives_pkey PRIMARY KEY (id);


--
-- Name: documents_geometries_archives documents_geometries_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries_archives
    ADD CONSTRAINT documents_geometries_archives_pkey PRIMARY KEY (id);


--
-- Name: documents_geometries documents_geometries_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries
    ADD CONSTRAINT documents_geometries_pkey PRIMARY KEY (document_id);


--
-- Name: documents_locales_archives documents_locales_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales_archives
    ADD CONSTRAINT documents_locales_archives_pkey PRIMARY KEY (id);


--
-- Name: documents_locales documents_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales
    ADD CONSTRAINT documents_locales_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (document_id);


--
-- Name: documents_tags_log documents_tags_log_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags_log
    ADD CONSTRAINT documents_tags_log_pkey PRIMARY KEY (id);


--
-- Name: documents_tags documents_tags_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags
    ADD CONSTRAINT documents_tags_pkey PRIMARY KEY (user_id, document_id);


--
-- Name: documents_topics documents_topics_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_topics
    ADD CONSTRAINT documents_topics_pkey PRIMARY KEY (document_locale_id);


--
-- Name: documents_topics documents_topics_topic_id_key; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_topics
    ADD CONSTRAINT documents_topics_topic_id_key UNIQUE (topic_id);


--
-- Name: documents_versions documents_versions_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_pkey PRIMARY KEY (id);


--
-- Name: es_deleted_documents es_deleted_documents_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_deleted_documents
    ADD CONSTRAINT es_deleted_documents_pkey PRIMARY KEY (document_id);


--
-- Name: es_deleted_locales es_deleted_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_deleted_locales
    ADD CONSTRAINT es_deleted_locales_pkey PRIMARY KEY (document_id, lang);


--
-- Name: es_sync_status es_sync_status_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_sync_status
    ADD CONSTRAINT es_sync_status_pkey PRIMARY KEY (id);


--
-- Name: feed_document_changes feed_document_changes_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_pkey PRIMARY KEY (change_id);


--
-- Name: feed_filter_area feed_filter_area_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_filter_area
    ADD CONSTRAINT feed_filter_area_pkey PRIMARY KEY (area_id, user_id);


--
-- Name: feed_followed_users feed_followed_users_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_followed_users
    ADD CONSTRAINT feed_followed_users_pkey PRIMARY KEY (followed_user_id, follower_user_id);


--
-- Name: history_metadata history_metadata_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY history_metadata
    ADD CONSTRAINT history_metadata_pkey PRIMARY KEY (id);


--
-- Name: images_archives images_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY images_archives
    ADD CONSTRAINT images_archives_pkey PRIMARY KEY (id);


--
-- Name: images images_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY images
    ADD CONSTRAINT images_pkey PRIMARY KEY (document_id);


--
-- Name: langs langs_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY langs
    ADD CONSTRAINT langs_pkey PRIMARY KEY (lang);


--
-- Name: map_associations map_associations_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY map_associations
    ADD CONSTRAINT map_associations_pkey PRIMARY KEY (document_id, topo_map_id);


--
-- Name: maps_archives maps_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY maps_archives
    ADD CONSTRAINT maps_archives_pkey PRIMARY KEY (id);


--
-- Name: maps maps_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY maps
    ADD CONSTRAINT maps_pkey PRIMARY KEY (document_id);


--
-- Name: outings_archives outings_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_archives
    ADD CONSTRAINT outings_archives_pkey PRIMARY KEY (id);


--
-- Name: outings_locales_archives outings_locales_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_locales_archives
    ADD CONSTRAINT outings_locales_archives_pkey PRIMARY KEY (id);


--
-- Name: outings_locales outings_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_locales
    ADD CONSTRAINT outings_locales_pkey PRIMARY KEY (id);


--
-- Name: outings outings_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings
    ADD CONSTRAINT outings_pkey PRIMARY KEY (document_id);


--
-- Name: routes_archives routes_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_archives
    ADD CONSTRAINT routes_archives_pkey PRIMARY KEY (id);


--
-- Name: routes_locales_archives routes_locales_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_locales_archives
    ADD CONSTRAINT routes_locales_archives_pkey PRIMARY KEY (id);


--
-- Name: routes_locales routes_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_locales
    ADD CONSTRAINT routes_locales_pkey PRIMARY KEY (id);


--
-- Name: routes routes_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (document_id);


--
-- Name: stopareas stopareas_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY stopareas
    ADD CONSTRAINT stopareas_pkey PRIMARY KEY (stoparea_id);


--
-- Name: documents_archives uq_documents_archives_document_id_version; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_archives
    ADD CONSTRAINT uq_documents_archives_document_id_version UNIQUE (version, document_id);


--
-- Name: documents_geometries_archives uq_documents_geometries_archives_document_id_version_lang; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries_archives
    ADD CONSTRAINT uq_documents_geometries_archives_document_id_version_lang UNIQUE (version, document_id);


--
-- Name: documents_locales_archives uq_documents_locales_archives_document_id_version_lang; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales_archives
    ADD CONSTRAINT uq_documents_locales_archives_document_id_version_lang UNIQUE (version, document_id, lang);


--
-- Name: waypoints_stopareas uq_waypoints_stopareas; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_stopareas
    ADD CONSTRAINT uq_waypoints_stopareas UNIQUE (stoparea_id, waypoint_id);


--
-- Name: user_profiles_archives user_profiles_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY user_profiles_archives
    ADD CONSTRAINT user_profiles_archives_pkey PRIMARY KEY (id);


--
-- Name: user_profiles user_profiles_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY user_profiles
    ADD CONSTRAINT user_profiles_pkey PRIMARY KEY (document_id);


--
-- Name: waypoints_archives waypoints_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_archives
    ADD CONSTRAINT waypoints_archives_pkey PRIMARY KEY (id);


--
-- Name: waypoints_locales_archives waypoints_locales_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_locales_archives
    ADD CONSTRAINT waypoints_locales_archives_pkey PRIMARY KEY (id);


--
-- Name: waypoints_locales waypoints_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_locales
    ADD CONSTRAINT waypoints_locales_pkey PRIMARY KEY (id);


--
-- Name: waypoints waypoints_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints
    ADD CONSTRAINT waypoints_pkey PRIMARY KEY (document_id);


--
-- Name: waypoints_stopareas waypoints_stopareas_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_stopareas
    ADD CONSTRAINT waypoints_stopareas_pkey PRIMARY KEY (waypoint_stoparea_id);


--
-- Name: xreports_archives xreports_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_archives
    ADD CONSTRAINT xreports_archives_pkey PRIMARY KEY (id);


--
-- Name: xreports_locales_archives xreports_locales_archives_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_locales_archives
    ADD CONSTRAINT xreports_locales_archives_pkey PRIMARY KEY (id);


--
-- Name: xreports_locales xreports_locales_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_locales
    ADD CONSTRAINT xreports_locales_pkey PRIMARY KEY (id);


--
-- Name: xreports xreports_pkey; Type: CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports
    ADD CONSTRAINT xreports_pkey PRIMARY KEY (document_id);


SET search_path = sympa, pg_catalog;

--
-- Name: subscriber_table subscriber_table_pkey; Type: CONSTRAINT; Schema: sympa; Owner: www-data
--

ALTER TABLE ONLY subscriber_table
    ADD CONSTRAINT subscriber_table_pkey PRIMARY KEY (list_subscriber, user_subscriber);


SET search_path = tracking, pg_catalog;

--
-- Name: activities activities_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_pkey PRIMARY KEY (id);


--
-- Name: migrations_lock migrations_lock_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY migrations_lock
    ADD CONSTRAINT migrations_lock_pkey PRIMARY KEY (index);


--
-- Name: migrations migrations_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY migrations
    ADD CONSTRAINT migrations_pkey PRIMARY KEY (id);


--
-- Name: polar polar_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY polar
    ADD CONSTRAINT polar_pkey PRIMARY KEY (id);


--
-- Name: strava strava_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY strava
    ADD CONSTRAINT strava_pkey PRIMARY KEY (id);


--
-- Name: users users_coros_id_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_coros_id_unique UNIQUE (coros_id);


--
-- Name: users users_garmin_token_secret_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_garmin_token_secret_unique UNIQUE (garmin_token_secret);


--
-- Name: users users_garmin_token_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_garmin_token_unique UNIQUE (garmin_token);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_pkey PRIMARY KEY (c2c_id);


--
-- Name: users users_polar_id_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_polar_id_unique UNIQUE (polar_id);


--
-- Name: users users_strava_id_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_strava_id_unique UNIQUE (strava_id);


--
-- Name: users users_suunto_username_unique; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY users
    ADD CONSTRAINT users_suunto_username_unique UNIQUE (suunto_username);


SET search_path = users, pg_catalog;

--
-- Name: sso_external_id sso_external_id_pkey; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY sso_external_id
    ADD CONSTRAINT sso_external_id_pkey PRIMARY KEY (domain, external_id);


--
-- Name: sso_key sso_key_key_key; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY sso_key
    ADD CONSTRAINT sso_key_key_key UNIQUE (key);


--
-- Name: sso_key sso_key_pkey; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY sso_key
    ADD CONSTRAINT sso_key_pkey PRIMARY KEY (domain);


--
-- Name: token token_pkey; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY token
    ADD CONSTRAINT token_pkey PRIMARY KEY (value);


--
-- Name: user user_email_key; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- Name: user user_forum_username_key; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_forum_username_key UNIQUE (forum_username);


--
-- Name: user user_pkey; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- Name: user user_username_key; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_username_key UNIQUE (username);


--
-- Name: user user_validation_nonce_key; Type: CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_validation_nonce_key UNIQUE (validation_nonce);


SET search_path = guidebook, pg_catalog;

--
-- Name: association_log_child_document_id_idx; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX association_log_child_document_id_idx ON association_log USING btree (child_document_id);


--
-- Name: association_log_parent_document_id_idx; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX association_log_parent_document_id_idx ON association_log USING btree (parent_document_id);


--
-- Name: association_log_user_id_idx; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX association_log_user_id_idx ON association_log USING btree (user_id);


--
-- Name: idx_documents_geometries_geom; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX idx_documents_geometries_geom ON documents_geometries USING gist (geom);


--
-- Name: idx_documents_geometries_geom_detail; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX idx_documents_geometries_geom_detail ON documents_geometries USING gist (geom_detail);


--
-- Name: idx_stopareas_geom; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX idx_stopareas_geom ON stopareas USING gist (geom);


--
-- Name: ix_guidebook_association_log_written_at; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_association_log_written_at ON association_log USING btree (written_at);


--
-- Name: ix_guidebook_associations_child_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_associations_child_document_id ON associations USING btree (child_document_id);


--
-- Name: ix_guidebook_associations_child_document_type; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_associations_child_document_type ON associations USING btree (child_document_type);


--
-- Name: ix_guidebook_associations_parent_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_associations_parent_document_id ON associations USING btree (parent_document_id);


--
-- Name: ix_guidebook_associations_parent_document_type; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_associations_parent_document_type ON associations USING btree (parent_document_type);


--
-- Name: ix_guidebook_documents_archives_type; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_archives_type ON documents_archives USING btree (type);


--
-- Name: ix_guidebook_documents_locales_archives_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_locales_archives_document_id ON documents_locales_archives USING btree (document_id);


--
-- Name: ix_guidebook_documents_locales_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_locales_document_id ON documents_locales USING btree (document_id);


--
-- Name: ix_guidebook_documents_tags_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_tags_document_id ON documents_tags USING btree (document_id);


--
-- Name: ix_guidebook_documents_tags_document_type; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_tags_document_type ON documents_tags USING btree (document_type);


--
-- Name: ix_guidebook_documents_tags_log_written_at; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_tags_log_written_at ON documents_tags_log USING btree (written_at);


--
-- Name: ix_guidebook_documents_tags_user_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_tags_user_id ON documents_tags USING btree (user_id);


--
-- Name: ix_guidebook_documents_type; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_type ON documents USING btree (type);


--
-- Name: ix_guidebook_documents_versions_document_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_versions_document_id ON documents_versions USING btree (document_id);


--
-- Name: ix_guidebook_documents_versions_history_metadata_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_documents_versions_history_metadata_id ON documents_versions USING btree (history_metadata_id);


--
-- Name: ix_guidebook_es_deleted_documents_deleted_at; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_es_deleted_documents_deleted_at ON es_deleted_documents USING btree (deleted_at);


--
-- Name: ix_guidebook_es_deleted_locales_deleted_at; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_es_deleted_locales_deleted_at ON es_deleted_locales USING btree (deleted_at);


--
-- Name: ix_guidebook_feed_document_changes_time_and_change_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_feed_document_changes_time_and_change_id ON feed_document_changes USING btree ("time" DESC, change_id);


--
-- Name: ix_guidebook_feed_filter_area_user_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_feed_filter_area_user_id ON feed_filter_area USING btree (user_id);


--
-- Name: ix_guidebook_history_metadata_user_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_history_metadata_user_id ON history_metadata USING btree (user_id);


--
-- Name: ix_guidebook_history_metadata_written_at; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_history_metadata_written_at ON history_metadata USING btree (written_at);


--
-- Name: ix_guidebook_routes_main_waypoint_id; Type: INDEX; Schema: guidebook; Owner: www-data
--

CREATE INDEX ix_guidebook_routes_main_waypoint_id ON routes USING btree (main_waypoint_id);


SET search_path = users, pg_catalog;

--
-- Name: ix_users_token_expire; Type: INDEX; Schema: users; Owner: www-data
--

CREATE INDEX ix_users_token_expire ON token USING btree (expire);


--
-- Name: ix_users_user_email_validated; Type: INDEX; Schema: users; Owner: www-data
--

CREATE INDEX ix_users_user_email_validated ON "user" USING btree (email_validated);


--
-- Name: ix_users_user_last_modified; Type: INDEX; Schema: users; Owner: www-data
--

CREATE INDEX ix_users_user_last_modified ON "user" USING btree (last_modified);


SET search_path = guidebook, pg_catalog;

--
-- Name: areas guidebook_areas_delete; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_areas_delete AFTER DELETE ON areas FOR EACH ROW EXECUTE PROCEDURE check_feed_area_ids();


--
-- Name: cache_versions guidebook_cache_versions_update; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_cache_versions_update BEFORE UPDATE ON cache_versions FOR EACH ROW EXECUTE PROCEDURE update_cache_version_time();


--
-- Name: documents_geometries_archives guidebook_documents_geometries_archives_geometries_insert_or_up; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_documents_geometries_archives_geometries_insert_or_up BEFORE INSERT OR UPDATE OF geom_detail ON documents_geometries_archives FOR EACH ROW EXECUTE PROCEDURE simplify_geom_detail();


--
-- Name: documents_geometries guidebook_documents_geometries_insert_or_update; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_documents_geometries_insert_or_update BEFORE INSERT OR UPDATE OF geom_detail ON documents_geometries FOR EACH ROW EXECUTE PROCEDURE simplify_geom_detail();


--
-- Name: documents guidebook_documents_insert; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_documents_insert AFTER INSERT ON documents FOR EACH ROW EXECUTE PROCEDURE create_cache_version();


--
-- Name: feed_document_changes guidebook_feed_document_changes_insert; Type: TRIGGER; Schema: guidebook; Owner: www-data
--

CREATE TRIGGER guidebook_feed_document_changes_insert AFTER INSERT OR UPDATE ON feed_document_changes FOR EACH ROW EXECUTE PROCEDURE check_feed_ids();


SET search_path = users, pg_catalog;

--
-- Name: user users_email_update; Type: TRIGGER; Schema: users; Owner: www-data
--

CREATE TRIGGER users_email_update AFTER UPDATE ON "user" FOR EACH ROW WHEN (((old.email)::text IS DISTINCT FROM (new.email)::text)) EXECUTE PROCEDURE update_mailinglists_email();


--
-- Name: user users_user_delete; Type: TRIGGER; Schema: users; Owner: www-data
--

CREATE TRIGGER users_user_delete AFTER DELETE ON "user" FOR EACH ROW EXECUTE PROCEDURE guidebook.check_feed_user_ids();


SET search_path = guidebook, pg_catalog;

--
-- Name: area_associations area_associations_area_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY area_associations
    ADD CONSTRAINT area_associations_area_id_fkey FOREIGN KEY (area_id) REFERENCES areas(document_id);


--
-- Name: area_associations area_associations_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY area_associations
    ADD CONSTRAINT area_associations_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: areas_archives areas_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY areas_archives
    ADD CONSTRAINT areas_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: areas areas_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY areas
    ADD CONSTRAINT areas_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: articles_archives articles_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY articles_archives
    ADD CONSTRAINT articles_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: articles articles_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY articles
    ADD CONSTRAINT articles_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: association_log association_log_child_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY association_log
    ADD CONSTRAINT association_log_child_document_id_fkey FOREIGN KEY (child_document_id) REFERENCES documents(document_id);


--
-- Name: association_log association_log_parent_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY association_log
    ADD CONSTRAINT association_log_parent_document_id_fkey FOREIGN KEY (parent_document_id) REFERENCES documents(document_id);


--
-- Name: association_log association_log_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY association_log
    ADD CONSTRAINT association_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: associations associations_child_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY associations
    ADD CONSTRAINT associations_child_document_id_fkey FOREIGN KEY (child_document_id) REFERENCES documents(document_id);


--
-- Name: associations associations_parent_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY associations
    ADD CONSTRAINT associations_parent_document_id_fkey FOREIGN KEY (parent_document_id) REFERENCES documents(document_id);


--
-- Name: books_archives books_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY books_archives
    ADD CONSTRAINT books_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: books books_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY books
    ADD CONSTRAINT books_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: cache_versions cache_versions_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY cache_versions
    ADD CONSTRAINT cache_versions_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_archives documents_archives_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_archives
    ADD CONSTRAINT documents_archives_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_archives documents_archives_redirects_to_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_archives
    ADD CONSTRAINT documents_archives_redirects_to_fkey FOREIGN KEY (redirects_to) REFERENCES documents(document_id);


--
-- Name: documents_geometries_archives documents_geometries_archives_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries_archives
    ADD CONSTRAINT documents_geometries_archives_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_geometries documents_geometries_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_geometries
    ADD CONSTRAINT documents_geometries_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_locales_archives documents_locales_archives_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales_archives
    ADD CONSTRAINT documents_locales_archives_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_locales_archives documents_locales_archives_lang_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales_archives
    ADD CONSTRAINT documents_locales_archives_lang_fkey FOREIGN KEY (lang) REFERENCES langs(lang);


--
-- Name: documents_locales documents_locales_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales
    ADD CONSTRAINT documents_locales_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_locales documents_locales_lang_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_locales
    ADD CONSTRAINT documents_locales_lang_fkey FOREIGN KEY (lang) REFERENCES langs(lang);


--
-- Name: documents documents_redirects_to_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents
    ADD CONSTRAINT documents_redirects_to_fkey FOREIGN KEY (redirects_to) REFERENCES documents(document_id);


--
-- Name: documents_tags documents_tags_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags
    ADD CONSTRAINT documents_tags_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_tags_log documents_tags_log_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags_log
    ADD CONSTRAINT documents_tags_log_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_tags_log documents_tags_log_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags_log
    ADD CONSTRAINT documents_tags_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: documents_tags documents_tags_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_tags
    ADD CONSTRAINT documents_tags_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: documents_topics documents_topics_document_locale_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_topics
    ADD CONSTRAINT documents_topics_document_locale_id_fkey FOREIGN KEY (document_locale_id) REFERENCES documents_locales(id);


--
-- Name: documents_versions documents_versions_document_archive_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_document_archive_id_fkey FOREIGN KEY (document_archive_id) REFERENCES documents_archives(id);


--
-- Name: documents_versions documents_versions_document_geometry_archive_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_document_geometry_archive_id_fkey FOREIGN KEY (document_geometry_archive_id) REFERENCES documents_geometries_archives(id);


--
-- Name: documents_versions documents_versions_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: documents_versions documents_versions_document_locales_archive_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_document_locales_archive_id_fkey FOREIGN KEY (document_locales_archive_id) REFERENCES documents_locales_archives(id);


--
-- Name: documents_versions documents_versions_history_metadata_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_history_metadata_id_fkey FOREIGN KEY (history_metadata_id) REFERENCES history_metadata(id);


--
-- Name: documents_versions documents_versions_lang_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY documents_versions
    ADD CONSTRAINT documents_versions_lang_fkey FOREIGN KEY (lang) REFERENCES langs(lang);


--
-- Name: es_deleted_locales es_deleted_locales_lang_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY es_deleted_locales
    ADD CONSTRAINT es_deleted_locales_lang_fkey FOREIGN KEY (lang) REFERENCES langs(lang);


--
-- Name: feed_document_changes feed_document_changes_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: feed_document_changes feed_document_changes_image1_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_image1_id_fkey FOREIGN KEY (image1_id) REFERENCES images(document_id);


--
-- Name: feed_document_changes feed_document_changes_image2_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_image2_id_fkey FOREIGN KEY (image2_id) REFERENCES images(document_id);


--
-- Name: feed_document_changes feed_document_changes_image3_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_image3_id_fkey FOREIGN KEY (image3_id) REFERENCES images(document_id);


--
-- Name: feed_document_changes feed_document_changes_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_document_changes
    ADD CONSTRAINT feed_document_changes_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: feed_filter_area feed_filter_area_area_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_filter_area
    ADD CONSTRAINT feed_filter_area_area_id_fkey FOREIGN KEY (area_id) REFERENCES areas(document_id);


--
-- Name: feed_filter_area feed_filter_area_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_filter_area
    ADD CONSTRAINT feed_filter_area_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: feed_followed_users feed_followed_users_followed_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_followed_users
    ADD CONSTRAINT feed_followed_users_followed_user_id_fkey FOREIGN KEY (followed_user_id) REFERENCES users."user"(id);


--
-- Name: feed_followed_users feed_followed_users_follower_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY feed_followed_users
    ADD CONSTRAINT feed_followed_users_follower_user_id_fkey FOREIGN KEY (follower_user_id) REFERENCES users."user"(id);


--
-- Name: history_metadata history_metadata_user_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY history_metadata
    ADD CONSTRAINT history_metadata_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


--
-- Name: images_archives images_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY images_archives
    ADD CONSTRAINT images_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: images images_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY images
    ADD CONSTRAINT images_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: map_associations map_associations_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY map_associations
    ADD CONSTRAINT map_associations_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: map_associations map_associations_topo_map_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY map_associations
    ADD CONSTRAINT map_associations_topo_map_id_fkey FOREIGN KEY (topo_map_id) REFERENCES maps(document_id);


--
-- Name: maps_archives maps_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY maps_archives
    ADD CONSTRAINT maps_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: maps maps_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY maps
    ADD CONSTRAINT maps_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: outings_archives outings_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_archives
    ADD CONSTRAINT outings_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: outings outings_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings
    ADD CONSTRAINT outings_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: outings_locales_archives outings_locales_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_locales_archives
    ADD CONSTRAINT outings_locales_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_locales_archives(id);


--
-- Name: outings_locales outings_locales_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY outings_locales
    ADD CONSTRAINT outings_locales_id_fkey FOREIGN KEY (id) REFERENCES documents_locales(id);


--
-- Name: routes_archives routes_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_archives
    ADD CONSTRAINT routes_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: routes_archives routes_archives_main_waypoint_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_archives
    ADD CONSTRAINT routes_archives_main_waypoint_id_fkey FOREIGN KEY (main_waypoint_id) REFERENCES documents(document_id);


--
-- Name: routes routes_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes
    ADD CONSTRAINT routes_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: routes_locales_archives routes_locales_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_locales_archives
    ADD CONSTRAINT routes_locales_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_locales_archives(id);


--
-- Name: routes_locales routes_locales_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes_locales
    ADD CONSTRAINT routes_locales_id_fkey FOREIGN KEY (id) REFERENCES documents_locales(id);


--
-- Name: routes routes_main_waypoint_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY routes
    ADD CONSTRAINT routes_main_waypoint_id_fkey FOREIGN KEY (main_waypoint_id) REFERENCES documents(document_id);


--
-- Name: user_profiles_archives user_profiles_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY user_profiles_archives
    ADD CONSTRAINT user_profiles_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: user_profiles user_profiles_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY user_profiles
    ADD CONSTRAINT user_profiles_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: waypoints_archives waypoints_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_archives
    ADD CONSTRAINT waypoints_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: waypoints waypoints_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints
    ADD CONSTRAINT waypoints_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: waypoints_locales_archives waypoints_locales_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_locales_archives
    ADD CONSTRAINT waypoints_locales_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_locales_archives(id);


--
-- Name: waypoints_locales waypoints_locales_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY waypoints_locales
    ADD CONSTRAINT waypoints_locales_id_fkey FOREIGN KEY (id) REFERENCES documents_locales(id);


--
-- Name: xreports_archives xreports_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_archives
    ADD CONSTRAINT xreports_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_archives(id);


--
-- Name: xreports xreports_document_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports
    ADD CONSTRAINT xreports_document_id_fkey FOREIGN KEY (document_id) REFERENCES documents(document_id);


--
-- Name: xreports_locales_archives xreports_locales_archives_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_locales_archives
    ADD CONSTRAINT xreports_locales_archives_id_fkey FOREIGN KEY (id) REFERENCES documents_locales_archives(id);


--
-- Name: xreports_locales xreports_locales_id_fkey; Type: FK CONSTRAINT; Schema: guidebook; Owner: www-data
--

ALTER TABLE ONLY xreports_locales
    ADD CONSTRAINT xreports_locales_id_fkey FOREIGN KEY (id) REFERENCES documents_locales(id);


SET search_path = sympa, pg_catalog;

--
-- Name: subscriber_table subscriber_table_user_id_fkey; Type: FK CONSTRAINT; Schema: sympa; Owner: www-data
--

ALTER TABLE ONLY subscriber_table
    ADD CONSTRAINT subscriber_table_user_id_fkey FOREIGN KEY (user_id) REFERENCES users."user"(id);


SET search_path = tracking, pg_catalog;

--
-- Name: activities activities_user_id_foreign; Type: FK CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY activities
    ADD CONSTRAINT activities_user_id_foreign FOREIGN KEY (user_id) REFERENCES users(c2c_id) ON DELETE CASCADE;


SET search_path = users, pg_catalog;

--
-- Name: sso_external_id sso_external_id_domain_fkey; Type: FK CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY sso_external_id
    ADD CONSTRAINT sso_external_id_domain_fkey FOREIGN KEY (domain) REFERENCES sso_key(domain);


--
-- Name: sso_external_id sso_external_id_user_id_fkey; Type: FK CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY sso_external_id
    ADD CONSTRAINT sso_external_id_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id);


--
-- Name: token token_userid_fkey; Type: FK CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY token
    ADD CONSTRAINT token_userid_fkey FOREIGN KEY (userid) REFERENCES "user"(id);


--
-- Name: user user_id_fkey; Type: FK CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_id_fkey FOREIGN KEY (id) REFERENCES guidebook.user_profiles(document_id);


--
-- Name: user user_lang_fkey; Type: FK CONSTRAINT; Schema: users; Owner: www-data
--

ALTER TABLE ONLY "user"
    ADD CONSTRAINT user_lang_fkey FOREIGN KEY (lang) REFERENCES guidebook.langs(lang);


--
-- PostgreSQL database dump complete
--

\unrestrict dgCt5Wiao4nhESbrgM0GjQgokAhHglngA7wNzWj88dF6NE1y2nTv3qvQeBkoCKc

