/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_import_events_import_events_post } from '../models/Body_import_events_import_events_post';
import type { Body_import_users_import_users_post } from '../models/Body_import_users_import_users_post';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ImportService {
    /**
     * Import Users
     * json cодержит список пользователей для импорта.
     * @param formData
     * @returns void
     * @throws ApiError
     */
    public static importUsersImportUsersPost(
        formData: Body_import_users_import_users_post,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/import/users',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Import Events
     * JSON содержит список мероприятий для импорта.
     * @param formData
     * @returns void
     * @throws ApiError
     */
    public static importEventsImportEventsPost(
        formData: Body_import_events_import_events_post,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/import/events',
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
