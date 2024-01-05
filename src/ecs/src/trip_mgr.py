from fastapi import HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import json
import logging
from pydantic import BaseModel
from .utils import call_trip_mgr
from .auth_route_dependency import authenticate_request


class CreateTripRequest(BaseModel):
    start_date: int
    end_date: int
    location: str
    title: str
    description: str


class UserWantsToGoOnTripRequest(BaseModel):
    trip_id: int


class UserApproval(BaseModel):
    trip_id: int
    is_approved: bool
    user_id_to_update: int


class UserNoLongerWantsToAttend(BaseModel):
    trip_id: int


class UserDenied(BaseModel):
    trip_id: int
    user_id: int


class DeleteTripRequest(BaseModel):
    trip_id: int


def verify_current_user_is_admin(user_id, trip_id, lambda_client):
    """
    Throws 401 if the current user is not the admin of the specified trip, otherwise there are no external interactions.

    :param user_id: User ID of the user making the request.
    :type user_id: int
    :param trip_id: ID of trip in question.
    :type trip_id: int
    :param lambda_client: The lambda client.
    :type lambda_client: boto3.client
    :return: None

    :raises HTTPException: With status code 401 if the current user is not admin of specified trip.
    :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
    """
    verify_payload = json.dumps({
        'httpMethod': 'GET',
        'action': 'get_trip_info_by_id',
        'body': {
            'trip_id': trip_id
        }
    })

    verify_response_payload = call_trip_mgr(lambda_client, verify_payload)

    if user_id != verify_response_payload['body']['admin_id'] \
            and 200 == verify_response_payload['statusCode']:
        raise HTTPException(status_code=401, detail='Not authorised to make the change')


def trip_mgr(app, lambda_client):
    """
    Method that defines all trip mgr methods.
    """
    @app.post('/trip')
    async def create_trip(request: CreateTripRequest, user_id=Depends(authenticate_request)):
        """
        Creates a new trip.

        :param request: Is the body containing relevant data.
        :return: None

        :raises HTTPException: With status code 400 if the proposed dates are invalid.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            # To ensure that dates are safe, 7200 represents two hours and will prevent times being the same in date
            # ranges for safety when calling weather api
            two_hours = 7200
            request.end_date += two_hours
            if request.start_date > request.end_date:
                raise HTTPException(status_code=400, detail='Start date must be less than end date')
            elif request.start_date == request.end_date:
                # add two hours if they are the same
                request.end_date += two_hours

            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'create_trip',
                'body': {
                    'admin_id': user_id,
                    'start_date': request.start_date,
                    'end_date': request.end_date,
                    'location': request.location,
                    'title': request.title,
                    'description': request.description
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 201:
                pass
            else:
                logging.error('error while creating trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while creating user non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=201, content=content)

    @app.delete('/trip')
    async def delete_trip(request: DeleteTripRequest, user_id=Depends(authenticate_request)):
        """
        Deletes an existing trip.

        :param request: Is the body containing relevant data.
        :return: None

        :raises HTTPException: With status code 400 if the delete transaction failed.
        :raises HTTPException: With status code 401 if the current user is not admin of specified trip.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            verify_current_user_is_admin(user_id, request.trip_id, lambda_client)

            payload = json.dumps({
                'httpMethod': 'DELETE',
                'action': 'delete_trip',
                'body': {
                    'trip_id': request.trip_id,
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                pass
            elif status_code == 400:
                HTTPException(status_code=400, detail='Transaction failed')
            else:
                logging.error('error while deleting trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while deleting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.get('/trips')
    async def get_trips(trip_id: Optional[int] = None,
                        location: Optional[str] = None,
                        admin_id: Optional[int] = None,
                        user_id=Depends(authenticate_request)):
        """
        Gets a trip by a specified parameter in the url. If no parameter is specified all trips will be returned.

        :param trip_id: (Optional) gets the trip by trip_id.
        :type trip_id: int
        :param location: (Optional) gets the trip by location.
        :type location: str
        :param admin_id: (Optional) gets the trip by admin_id.
        :type admin_id: int
        :return: Within the body an Item or Items array containing the trip/s.

        :raises HTTPException: With status code 404 if no trip matching the description is found.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            payload = None

            if trip_id is not None:
                payload = json.dumps({
                    'httpMethod': 'GET',
                    'action': 'get_trip_info_by_id',
                    'body': {
                        'trip_id': trip_id
                    }
                })
            elif location is not None:
                payload = json.dumps({
                    'httpMethod': 'GET',
                    'action': 'get_trip_info_by_location',
                    'body': {
                        'location': location
                    }
                })
            elif admin_id is not None:
                payload = json.dumps({
                    'httpMethod': 'GET',
                    'action': 'get_trip_info_by_admin_id',
                    'body': {
                        'admin_id': admin_id
                    }
                })
            else:
                payload = json.dumps({
                    'httpMethod': 'GET',
                    'action': 'get_all_trips'
                })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                content = response_payload['body']
            elif status_code == 404:
                logging.error('Trips not found: ' + str(response_payload))
                raise HTTPException(status_code=404, detail='Trips not found')
            else:
                logging.error('error while getting trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.get('/trips-user-id')
    async def get_trips_user_id(user_id=Depends(authenticate_request)):
        """
        Gets a trip by the user_id specified in the headers.

        :return: Within the body an Item or Items array containing the trip/s.

        :raises HTTPException: With status code 404 if no trip matching the description is found.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'GET',
                'action': 'get_all_trips_for_user_id',
                'body': {
                    'user_id': user_id
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                content = response_payload['body']['items']
            elif status_code == 404:
                logging.error('Trips not found: ' + str(response_payload))
                raise HTTPException(status_code=404, detail='Trips not found')
            else:
                logging.error('error while getting trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.post('/user-wants-to-go-on-trip')
    async def user_wants_to_go_on_trip(request: UserWantsToGoOnTripRequest, user_id=Depends(authenticate_request)):
        """
        User specifies a trip that they would like to apply for.

        :return: None

        :raises HTTPException: With status code 400 the transaction failed,
                               commonly caused by a user already in the application process.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'user_wants_to_go_on_trip',
                'body': {
                    'user_id': user_id,
                    'trip_id': request.trip_id
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                pass
            elif status_code == 400:
                HTTPException(status_code=400,
                              detail='Transaction failed, likely caused by user already being in table')
            else:
                logging.error('error while updating trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.post('/user-approval')
    async def user_approval(request: UserApproval, user_id=Depends(authenticate_request)):
        """
        Admin of a trip approves a user for a trip.

        :return: None

        :raises HTTPException: With status code 400 the transaction failed.
        :raises HTTPException: With status code 401 if the current user is not admin of specified trip.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            verify_current_user_is_admin(user_id, request.trip_id, lambda_client)

            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'user_approval',
                'body': {
                    'user_id': request.user_id_to_update,
                    'trip_id': request.trip_id,
                    'is_approved': request.is_approved
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                pass
            elif status_code == 400:
                HTTPException(status_code=400, detail='Transaction failed')
            else:
                logging.error('error while updating trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.post('/user-no-longer-wants-to-attend')
    async def user_no_longer_wants_to_attend(request: UserNoLongerWantsToAttend, user_id=Depends(authenticate_request)):
        """
        User that has applied for a trip can resign from it, this works if they have been approved or not.

        :return: None

        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """

        content = None

        try:
            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'remove_user_application',
                'body': {
                    'user_id': user_id,
                    'trip_id': request.trip_id,
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                pass
            else:
                logging.error('error while updating trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)

    @app.post('/user-denied')
    async def user_no_longer_wants_to_attend(request: UserDenied, admin_id=Depends(authenticate_request)):
        """
        Admin can deny a user from being apart of a trip, even after being approved.

        :return: None

        :raises HTTPException: With status code 401 the current user must be the admin of the trip to remove the user.
        :raises HTTPException: With status code 500 in an internal error occurred.
        :raises HTTPException: With status code 502 if the lambda fails unexpectedly.
        """
        content = None

        try:
            # Get the admin id of the trip in question and validate request
            get_trip_payload = json.dumps({
                'httpMethod': 'GET',
                'action': 'get_trip_info_by_id',
                'body': {
                    'trip_id': request.trip_id
                }
            })

            trip_payload = call_trip_mgr(lambda_client, get_trip_payload)

            if trip_payload['statusCode'] != 200:
                raise HTTPException(status_code=500, detail='Failed to get trip')

            if admin_id != trip_payload['body']['admin_id']:
                print(admin_id)
                print(trip_payload['body']['admin_id'])
                raise HTTPException(status_code=401, detail='Not Authorized')

            # Remove user
            payload = json.dumps({
                'httpMethod': 'POST',
                'action': 'remove_user_application',
                'body': {
                    'user_id': request.user_id,
                    'trip_id': request.trip_id,
                }
            })

            response_payload = call_trip_mgr(lambda_client, payload)

            status_code = response_payload['statusCode']

            if status_code == 200:
                pass
            else:
                logging.error('error while updating trip returned non-201 response: ' + str(response_payload))
                raise HTTPException(status_code=500, detail='Error while getting trip non-201 response')

        except HTTPException as http_exception:
            raise http_exception
        except Exception as e:
            logging.error('invoking trip_mgr: ' + str(e))
            raise HTTPException(status_code=500, detail=str(e))

        return JSONResponse(status_code=200, content=content)
