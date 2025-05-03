/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventLevelCreateOrUpdate } from '../models/EventLevelCreateOrUpdate';
import type { EventLevelRead } from '../models/EventLevelRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EventsLevelsService {
    /**
     * Get Event Levels
     * @returns EventLevelRead Successful Response
     * @throws ApiError
     */
    public static getEventLevelsEventsLevelsGet(): CancelablePromise<Array<EventLevelRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/levels',
        });
    }
    /**
     * Create Event Level
     * @param requestBody
     * @returns EventLevelRead Successful Response
     * @throws ApiError
     */
    public static createEventLevelEventsLevelsPost(
        requestBody: EventLevelCreateOrUpdate,
    ): CancelablePromise<EventLevelRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events/levels',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Event Level
     * @param levelId
     * @param requestBody
     * @returns EventLevelRead Successful Response
     * @throws ApiError
     */
    public static updateEventLevelEventsLevelsLevelIdPut(
        levelId: string,
        requestBody: EventLevelCreateOrUpdate,
    ): CancelablePromise<EventLevelRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/events/levels/{level_id}',
            path: {
                'level_id': levelId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Event Level
     * @param levelId
     * @returns void
     * @throws ApiError
     */
    public static deleteEventLevelEventsLevelsLevelIdDelete(
        levelId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/events/levels/{level_id}',
            path: {
                'level_id': levelId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
