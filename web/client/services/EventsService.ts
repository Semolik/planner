/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventCreate } from '../models/EventCreate';
import type { EventFullInfo } from '../models/EventFullInfo';
import type { EventUpdate } from '../models/EventUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EventsService {
    /**
     * Get Actual Events
     * Получить список актуальных мероприятий.
     * @returns EventFullInfo Successful Response
     * @throws ApiError
     */
    public static getActualEventsEventsActualGet(): CancelablePromise<Array<EventFullInfo>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/actual',
        });
    }
    /**
     * Create Event
     * @param requestBody
     * @returns EventFullInfo Successful Response
     * @throws ApiError
     */
    public static createEventEventsPost(
        requestBody: EventCreate,
    ): CancelablePromise<EventFullInfo> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Events Token
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getEventsTokenEventsTokenGet(): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/token',
        });
    }
    /**
     * Get Event
     * @param eventId
     * @returns EventFullInfo Successful Response
     * @throws ApiError
     */
    public static getEventEventsEventIdGet(
        eventId: string,
    ): CancelablePromise<EventFullInfo> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/{event_id}',
            path: {
                'event_id': eventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Event
     * @param eventId
     * @param requestBody
     * @returns EventFullInfo Successful Response
     * @throws ApiError
     */
    public static updateEventEventsEventIdPut(
        eventId: string,
        requestBody: EventUpdate,
    ): CancelablePromise<EventFullInfo> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/events/{event_id}',
            path: {
                'event_id': eventId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Event
     * @param eventId
     * @returns void
     * @throws ApiError
     */
    public static deleteEventEventsEventIdDelete(
        eventId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/events/{event_id}',
            path: {
                'event_id': eventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Event History
     * @param eventId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getEventHistoryEventsEventIdHistoryGet(
        eventId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/{event_id}/history',
            path: {
                'event_id': eventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
