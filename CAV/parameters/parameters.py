



model_parameters = {

    'first_year'                                        :   2018                    ,
    'current_freeway_vmt'                               :   39000000                ,
    'current_arterial_vmt'                              :   45000000                ,

    'city truck share_vmt'                              :	0.1                     ,
    'growth_rate'                                       :	0.015                   ,

    'downtown_at'                                       :	0.1                     ,
    'urban_at'                                          :	0.25                    ,
    'suburban_business_at'                              :	0.1                     ,
    'suburban_residential_at'                           :	0.4                     ,
    'rural_at'                                          :	0.15                    ,
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
    'downtown_%_congested'                              :	0.8                     ,
    'urban_%_congested'                                 :	0.5                     ,
    'suburban_business_%_congested'                     :	0.4                     ,
    'suburban_residential_%_congested'                  :	0.2                     ,
    'rural_%_congested'                                 :	0.1                     ,
    'downtown_free_speed'                               :	20                      ,
    'urban_free_speed'                                  :	25                      ,
    'suburban_business_free_speed'                      :	30                      ,
    'suburban_residential_free_speed'                   :	45                      ,
    'rural_free_speed'                                  :	55                      ,
    'non-licensed_adult_trip_spending'                  :	13.4                    ,
    'handicapped_and_elderly_trip_spending'             :	15.2                    ,
    'unaccompanied_children_trip_spending'              :	14.5                    ,
    'travel_time_index_-_freeway_share'                 :	0.7                     ,
    'freeway_planning_index_-_freeway_share'            :	0.3                     ,
    'travel_time_index_-_arterial_share'                :	0.9                     ,
    'freeway_planning_index_-_arterial_share'           :	0.1                     ,
    'travel_time_index_-_area_type_share'               :	0.85                    ,
    'freeway_planning_index_-_area_type_share'          :	0.15                    ,
    'high_skill_jobs_-_winners'                         :	173220                  ,
    'medium_skill_jobs_-_winners'                       :	2030                    ,
    'low_skill_jobs_-_winners'                          :	15070                   ,
    'high_skill_mean_salary_-_winners'                  :	108573                  ,
    'medium_skill_mean_salary_-_winners'                :	57657                   ,
    'low_skill_mean_salary_-_winners'                   :	31516                   ,
    'high_skill_jobs_-_losers'                          :	75120                   ,
    'medium_skill_jobs_-_losers'                        :	66030                   ,
    'low_skill_jobs_-_losers'                           :	144710                  ,
    'high_skill_mean_salary_-_losers'                   :	128117                  ,
    'medium_skill_mean_salary_-_losers'                 :	60085                   ,
    'low_skill_mean_salary_-_losers'                    :	31111                   ,
    'high_skill_jobs_-_%_lost'                          :	0.416174121405751       ,
    'medium_skill_jobs_-_%_lost'                        :	0.428381038921702       ,
    'low_skill_jobs_-_%_lost'                           :	0.366242830488563


}

area types = sum(b10:b14)
time of day	=sum(b16:b17)
winners	=sum(b47:b49)
high	=b80/b33
medium	=b81/b33
low	=b82/b33
losers	=sum(b51:b53)
high	=b86/b33
medium	=b87/b33
low	=b88/b33
current freeway vmt share	=b4/b6
current arterial vmt share	=b5/b6