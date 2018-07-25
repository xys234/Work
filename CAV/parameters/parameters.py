
from math import isclose

model_parameters = {

    'first_year'                                        : 2018                      ,
    'current_freeway_vmt'                               : 39000000                  ,
    'current_arterial_vmt'                              : 45000000                  ,
    'city truck share_vmt'                              :	0.1                     ,
    'growth_rate'                                       :	0.015                   ,
    'downtown_AT'                                       :	0.1                     ,
    'urban_AT'                                          :	0.25                    ,
    'suburban_business_AT'                              :	0.1                     ,
    'suburban_residential_AT'                           :	0.4                     ,
    'rural_AT'                                          :	0.15                    ,
    'peak_period'                                       :   0.35                    ,
    'offpeak_period'                                    :   0.65                    ,
    'non_licensed_adult'                                :	0.1                     ,
    'handicapped_and_elderly'                           :	0.15                    ,
    'unaccompanied_children'                            :	0.25                    ,
    'percent_peak_vmt'                                  :	0.45                    ,
    'percent_lane_miles'                                :	0.35                    ,
    'number of hours'                                   :	5                       ,
    'travel time index'                                 :	1.34                    ,
    'freeway_planning_index'                            :	3.48                    ,
    'freeway_free_speed'                                :	60                      ,
    'arterial_free_speed'                               :	25                      ,
    'household_vehicle_fleet'                           :	3600000                 ,
    'current_households'                                :	2160000                 ,
    'current_population'                                :	6010000                 ,
    'current_employment'                                :	3420000                 ,
    'vehicle_replacement_rate'                          :	0.071                   ,
    'region'                                            :	'northeast'             ,
    'parking_revenues'                                  :	40.04                   ,
    'parking_fines'                                     :	34.57                   ,
    'traffic_citations'                                 :	4.77                    ,
    'camera'                                            :	11.05                   ,
    'towing'                                            :	2.17                    ,
    'gas_tax'                                           :	18.59                   ,
    'licensing'                                         :	6.1                     ,
    'registration'                                      :	11.89                   ,
    'downtown_ridesource_offset'                        :	0                       ,
    'urban_ridesource_offset'                           :	3                       ,
    'suburban_business_ridesource_offset'               :	5                       ,
    'suburban_residential_ridesource_offset'            :	8                       ,
    'rural_ridesource_offset'                           :	17                      ,
    'downtown_percent_congested'                              :	0.8                     ,
    'urban_percent_congested'                                 :	0.5                     ,
    'suburban_business_percent_congested'                     :	0.4                     ,
    'suburban_residential_percent_congested'                  :	0.2                     ,
    'rural_percent_congested'                                 :	0.1                     ,
    'downtown_free_speed'                               :	20                      ,
    'urban_free_speed'                                  :	25                      ,
    'suburban_business_free_speed'                      :	30                      ,
    'suburban_residential_free_speed'                   :	45                      ,
    'rural_free_speed'                                  :	55                      ,
    'non-licensed_adult_trip_spending'                  :	13.4                    ,
    'handicapped_and_elderly_trip_spending'             :	15.2                    ,
    'unaccompanied_children_trip_spending'              :	14.5                    ,
    'travel_time_index_freeway_share'                 :	0.7                     ,
    'freeway_planning_index_freeway_share'            :	0.3                     ,
    'travel_time_index_arterial_share'                :	0.9                     ,
    'freeway_planning_index_arterial_share'           :	0.1                     ,
    'travel_time_index_area_type_share'               :	0.85                    ,
    'freeway_planning_index_area_type_share'          :	0.15                    ,
    'high_skill_jobs_winners'                         :	173220                  ,
    'medium_skill_jobs_winners'                       :	2030                    ,
    'low_skill_jobs_winners'                          :	15070                   ,
    'high_skill_mean_salary_winners'                  :	108573                  ,
    'medium_skill_mean_salary_winners'                :	57657                   ,
    'low_skill_mean_salary_winners'                   :	31516                   ,
    'high_skill_jobs_losers'                          :	75120                   ,
    'medium_skill_jobs_losers'                        :	66030                   ,
    'low_skill_jobs_losers'                           :	144710                  ,
    'high_skill_mean_salary_losers'                   :	128117                  ,
    'medium_skill_mean_salary_losers'                 :	60085                   ,
    'low_skill_mean_salary_losers'                    :	31111                   ,
    'high_skill_jobs_percent_lost'                          :	0.416174121405751,
    'medium_skill_jobs_percent_lost'                        :	0.428381038921702,
    'low_skill_jobs_percent_lost'                           :	0.366242830488563,

    'VMT_fee'                                         :0.05,                 # per mile
    'NOVMT_fee'                                       :0.10,
    'pricing'                                         :0.10,

    'percent_auto_drive': {
                                'car1'  : {'freeway': 0.0, 'arterial': 0.0},
                                'car2'  : {'freeway': 0.5, 'arterial': 0.5},
                                'car3'  : {'freeway': 1.0, 'arterial': 1.0},
                                'truck1': {'freeway': 0.0, 'arterial': 0.0},
                                'truck2': {'freeway': 0.5, 'arterial': 0.5},
                                'truck3': {'freeway': 1.0, 'arterial': 1.0},

                           },

    'auto_assistance':  {
                             'standard': 0.0,
                             'type1': 0.0,
                             'type2': 0.3,
                             'type3': 1.0
    },

    'cost_reduction_auto_truck': {

        'midwest':      {'high':0.105, 'low':0.079},
        'northeast':    {'high':0.105, 'low':0.079},
        'southeast':    {'high':0.115, 'low':0.086},
        'southwest':    {'high':0.101, 'low':0.076},
        'west':         {'high':0.105, 'low':0.079},

    }

}


def derive_parameters(param):
    '''

    :param model_parameter:
    :return: update the model_parameter with derived parameters
    '''

    # Checks
    assert isclose(sum([param['downtown_AT'], param['urban_AT'], param['suburban_business_AT'],
                       param['suburban_residential_AT'], param['rural_AT']]), 1.0), \
                       'Area type percentages must add up to 1.0'

    assert isclose(sum([param['peak_period']+param['offpeak_period']]), 1.0), 'Period percentages must add up to 1.0'

    # additional parameters
    param['winners_high'] = param['high_skill_jobs_winners'] / param['current_employment']
    param['winners_medium'] = param['medium_skill_jobs_winners'] / param['current_employment']
    param['winners_low'] = param['low_skill_jobs_winners'] / param['current_employment']

    param['losers_high'] = param['high_skill_jobs_losers'] / param['current_employment']
    param['losers_medium'] = param['medium_skill_jobs_losers'] / param['current_employment']
    param['losers_low'] = param['low_skill_jobs_losers'] / param['current_employment']

    param['winners'] = param['winners_high'] + param['winners_medium'] + param['winners_low']
    param['losers'] = param['losers_high'] + param['losers_medium'] + param['losers_low']

    param['current_total_vmt'] = param['current_freeway_vmt'] + param['current_arterial_vmt']
    param['current_freeway_vmt_share'] = param['current_freeway_vmt'] * 1.0 / param['current_total_vmt']
    param['current_arterial_vmt_share'] = param['current_arterial_vmt'] * 1.0 / param['current_total_vmt']


    # year weights
    param['year_weights'] = {}
    for t in ['car1', 'car2', 'car3', 'truck1', 'truck2', 'truck3']:
        for f in ['freeway', 'arterial']:
            if param['percent_auto_drive'][t][f] > 0:
                if t in ('car1', 'car2', 'car3'):
                    param['year_weights'][(t,f)] = \
                        (1.0 - param['city truck share_vmt']) / param['percent_auto_drive'][t][f]
                else:
                    param['year_weights'][(t, f)] = \
                        param['city truck share_vmt'] / param['percent_auto_drive'][t][f]
            else:
                param['year_weights'][(t, f)] = 0.0

    return param


def get_congestion_stats(model_parameters):
    '''

    :param model_parameters:
    :return:
    '''




if __name__=='__main__':

    model_parameters = derive_parameters(model_parameters)
    for k, v in model_parameters.items():
        if isinstance(v, str):
            print(k.ljust(50) + ":{0}".format(v))
        elif isinstance(v, (list, dict)):
            print(k.ljust(50) + str(v))
        else:
            print(k.ljust(50) + "{0:.4f}".format(v))