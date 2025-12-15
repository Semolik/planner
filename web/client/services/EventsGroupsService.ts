/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupCreate } from '../models/EventGroupCreate';
import type { EventGroupRead } from '../models/EventGroupRead';
import type { EventGroupReadShort } from '../models/EventGroupReadShort';
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
     * Convert Event Group To Aggregated
     * @param groupId
     * @param isSingleAlbum
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static convertEventGroupToAggregatedEventsGroupsGroupIdConvertToAggregatedPost(
        groupId: string,
        isSingleAlbum: boolean,
    ): CancelablePromise<EventGroupRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events/groups/{group_id}/convert-to-aggregated',
            path: {
                'group_id': groupId,
            },
            query: {
                'is_single_album': isSingleAlbum,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Remove Aggregation From Event Group
     * @param groupId
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static removeAggregationFromEventGroupEventsGroupsGroupIdRemoveAggregationPost(
        groupId: string,
    ): CancelablePromise<EventGroupRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/events/groups/{group_id}/remove-aggregation',
            path: {
                'group_id': groupId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Search Event Groups
     * @param query
     * @param page
     * @param filter
     * @param withAggregateTask
     * @returns EventGroupReadShort Successful Response
     * @throws ApiError
     */
    public static searchEventGroupsEventsGroupsSearchGet(
        query?: string,
        page: number = 1,
        filter: 'all' | 'active' | 'passed' = 'all',
        withAggregateTask?: (boolean | null),
    ): CancelablePromise<Array<EventGroupReadShort>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/events/groups/search',
            query: {
                'query': query,
                'page': page,
                'filter': filter,
                'with_aggregate_task': withAggregateTask,
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
     * Update Event Group
     * @param groupId
     * @param requestBody
     * @returns EventGroupRead Successful Response
     * @throws ApiError
     */
    public static updateEventGroupEventsGroupsGroupIdPut(
        groupId: string,
        requestBody: EventGroupCreate,
    ): CancelablePromise<EventGroupRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/events/groups/{group_id}',
            path: {
                'group_id': groupId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
