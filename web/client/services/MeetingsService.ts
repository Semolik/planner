/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MeetingCreate } from '../models/MeetingCreate';
import type { MeetingRead } from '../models/MeetingRead';
import type { MeetingUpdate } from '../models/MeetingUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class MeetingsService {
    /**
     * Get Meetings
     * @returns MeetingRead Successful Response
     * @throws ApiError
     */
    public static getMeetingsMeetingsGet(): CancelablePromise<Array<MeetingRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/meetings',
        });
    }
    /**
     * Create Meeting
     * @param requestBody
     * @returns MeetingRead Successful Response
     * @throws ApiError
     */
    public static createMeetingMeetingsPost(
        requestBody: MeetingCreate,
    ): CancelablePromise<MeetingRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/meetings',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Meeting
     * @param meetingId
     * @param requestBody
     * @returns MeetingRead Successful Response
     * @throws ApiError
     */
    public static updateMeetingMeetingsMeetingIdPut(
        meetingId: string,
        requestBody: MeetingUpdate,
    ): CancelablePromise<MeetingRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/meetings/{meeting_id}',
            path: {
                'meeting_id': meetingId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Meeting
     * @param meetingId
     * @returns void
     * @throws ApiError
     */
    public static deleteMeetingMeetingsMeetingIdDelete(
        meetingId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/meetings/{meeting_id}',
            path: {
                'meeting_id': meetingId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Meeting
     * @param meetingId
     * @returns MeetingRead Successful Response
     * @throws ApiError
     */
    public static getMeetingMeetingsMeetingIdGet(
        meetingId: string,
    ): CancelablePromise<MeetingRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/meetings/{meeting_id}',
            path: {
                'meeting_id': meetingId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
