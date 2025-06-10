/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupCreate } from '../models/EventGroupCreate';
import type { EventGroupRead } from '../models/EventGroupRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class EventsGroupsService {
    /**
     * Create Event Group
     * @param requestBody
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static createEventGroupEventsGroupsPost(
        requestBody: EventGroupCreate,
    ): CancelablePromise<EventGroupRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events/groups',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Search Event Groups
     * @param query
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static searchEventGroupsEventsGroupsSearchGet(
        query?: string,
    ): CancelablePromise<Array<EventGroupRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/groups/search',
            query: {
                'query': query,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Event Group
     * @param groupId
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static getEventGroupEventsGroupsGroupIdGet(
        groupId: string,
    ): CancelablePromise<EventGroupRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Event Group
     * @param groupId
     * @param removeEvents
     * @returns void
     * @throws ApiError
     */
    public static deleteEventGroupEventsGroupsGroupIdDelete(
        groupId: string,
        removeEvents: boolean = false,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/events/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            query: {
                'remove_events': removeEvents,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add Event To Group
     * @param groupId
     * @param eventId
     * @returns void
     * @throws ApiError
     */
    public static addEventToGroupEventsGroupsGroupIdEventsEventIdPost(
        groupId: string,
        eventId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events/groups/{group_id}/events/{event_id}',
            path: {
                'group_id': groupId,
                'event_id': eventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Remove Event From Group
     * @param groupId
     * @param eventId
     * @returns void
     * @throws ApiError
     */
    public static removeEventFromGroupEventsGroupsGroupIdEventsEventIdDelete(
        groupId: string,
        eventId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/events/groups/{group_id}/events/{event_id}',
            path: {
                'group_id': groupId,
                'event_id': eventId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
