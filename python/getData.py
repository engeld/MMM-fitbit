#!/usr/bin/env python
import fitbit
import json
from iniHandler import print_data, print_json, ReadCredentials, ReadTokens
from datetime import date
import json
from authHandler import *
import math

if __name__ == "__main__":
	ResourceTypes = ['steps', 'floors', 'caloriesOut']

	#This is the Fitbit URL to use for the API call
	FitbitURL = "https://api.fitbit.com/1/user/-/profile.json"

	#Get credentials
	ClientID, ClientSecret = ReadCredentials()

	APICallOK = False
	while not APICallOK:
		#Get tokens
		AccessToken, RefreshToken = ReadTokens()
		#Make the API call
		APICallOK, TokensOK, APIResponse = MakeAPICall(FitbitURL, AccessToken, RefreshToken)
		
		print_json('status',APIResponse)
		if not TokensOK:
			sys.exit(1)
	
	#Create authorised client and grab step count from one day of steps
	authdClient = fitbit.Fitbit(ClientID, ClientSecret, oauth2=True, access_token=AccessToken, refresh_token=RefreshToken)
	activityList = authdClient.activities()

	try:
		activitySummary = activityList['summary'] #Use for steps, floors, calories. Adapt for distance, active minutes
		activityGoals = activityList['goals'] #Goals for steps, floors, calories, distance, active minutes

		sleepSummary = authdClient.sleep()['summary']
		totalMinutesAsleep = sleepSummary['totalMinutesAsleep']

		heartTimeSeries = authdClient.time_series('activities/heart',period='1d')

		#Get Weight
		weight = authdClient.get_bodyweight()
		
		#Calculate active minutes
		activeMinutes = activitySummary['fairlyActiveMinutes'] + activitySummary['veryActiveMinutes']

		# Print all data
		for resource in ResourceTypes:
			print_data(resource,activitySummary[resource],activityGoals[resource])

		print_data('distance',activitySummary['distances'][0]['distance'],activityGoals['distance'])
		print_data('activeMinutes',activeMinutes,activityGoals['activeMinutes'])
		print_data('sleep',totalMinutesAsleep,480)

		# OK so the weight comes in this form (printed with print(weight['weight']))
		# [{u'weight': 154.3, u'bmi': 22.09, u'logId': 1528502399000, u'source': u'API', u'time': u'23:59:59', u'date': u'2018-06-08'}]
		#print(weight['weight'])
		#print(weight['weight'][0]['weight'])
		fitbit_weight_lbs = weight['weight'][0]['weight']
		fitbit_weight_kg = math.ceil(weight['weight'][0]['weight'] * 0.45359237)
		#print fitbit_weight_kg

		#for items in weight['weight']:
        #		print(items['weight']) 

		print_data('weight',fitbit_weight_kg,75)
		print_data('heart',heartTimeSeries['activities-heart'][0]['value']['restingHeartRate'],60)
		print("fuckthisshit")



	except KeyError as err:
		print_data(str(err).strip("'"),0,1)