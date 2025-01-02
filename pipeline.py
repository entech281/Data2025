import dlt
import tba
import motherduck
import util
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def everyone_use_the_same_logger():
    tba.set_logger(logger)
    return logger


@dlt.resource(table_name="teams", write_disposition='merge', primary_key='key')
def sync_teams_source(event_list):
    for event_name in event_list:
        yield from  tba.get_teams_for_event(event_name)


@dlt.resource(table_name='matches', write_disposition='merge', primary_key='key')
def sync_matches_source(event_list):
    for event_name in event_list:
        yield from tba.get_matches_for_event(event_name)


@dlt.resource(table_name='oprs', write_disposition='merge', primary_key=['team_number','event_key'])
def event_opr_source(event_list):
    for event_name in event_list:
        yield from tba.get_event_oprs(event_name)


@dlt.resource(table_name='event_rankings', write_disposition='merge', primary_key=['team_number','event_key'])
def event_rankings_source(event_list):
    for event_name in event_list:
        yield from tba.get_event_rankings(event_name)


@dlt.resource(table_name='district_rankings', write_disposition='merge', primary_key=['team_number','district_key'])
def district_rankings_source():
    # change this to DISTRICT_KEY='2025fsc' after the season starts
    yield from tba.get_rankings_for_district('2024pch')

@dlt.resource(table_name='match_predictions', write_disposition='merge', primary_key=['match_key','event_key'])
def event_predictions_source(event_list):
    for event_name in event_list:
        yield from tba.get_match_predictions_for_event(event_name)

@dlt.resource(table_name='event_scoring_components', write_disposition='merge', primary_key=['team_key','event_key','component'])
def event_scoring_components_source(event_list):
    for event_name in event_list:
        yield from tba.get_event_scoring_components(event_name)

def sync():


    pipeline = dlt.pipeline(
        pipeline_name='2025sc',
        destination='motherduck',
        dataset_name='tba'
    )

    #for 2025 event_list = [ '2025schar','2025sccha', '2025sccmp' ]
    event_list =  ['2024sccha','2024gacmp']

    logger.info("Teams...")
    load_info = pipeline.run(sync_teams_source(event_list))
    logger.info(load_info)

    logger.info("Matches...")
    load_info = pipeline.run(sync_matches_source(event_list))
    logger.info(load_info)

    logger.info("Match Predictions....")
    load_info = pipeline.run(event_predictions_source(event_list))
    logger.info(load_info)

    logger.info("Scoring Components....")
    load_info = pipeline.run(event_scoring_components_source(event_list))
    logger.info(load_info)

    logger.info("Rankings...")
    load_info = pipeline.run(event_rankings_source(event_list))
    logger.info(load_info)

    logger.info("District Rankings...")
    load_info = pipeline.run(district_rankings_source())
    logger.info(load_info)

    logger.info("Oprs...")
    load_info = pipeline.run(event_opr_source(event_list))
    logger.info(load_info)

    logger.warning("Sync Complete!")




if __name__ == '__main__':
    util.setup_logging()
    sync()

