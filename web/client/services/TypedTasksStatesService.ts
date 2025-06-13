/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ReadTypedTaskState } from '../models/ReadTypedTaskState';
import type { StatePeriod } from '../models/StatePeriod';
import type { UpdateTypedTaskState } from '../models/UpdateTypedTaskState';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TypedTasksStatesService {
    /**
     * Update User Typed Task State
     * @param typedTaskStateId
     * @param requestBody
     * @returns ReadTypedTaskState Successful Response
     * @throws ApiError
     */
    public static updateUserTypedTaskStateTasksTypedTasksStatesTypedTaskStateIdPut(
        typedTaskStateId: string,
        requestBody: UpdateTypedTaskState,
    ): CancelablePromise<ReadTypedTaskState> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/tasks/typed-tasks/states/{typed_task_state_id}',
            path: {
                'typed_task_state_id': typedTaskStateId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Typed Task State
     * @param typedTaskStateId
     * @returns void
     * @throws ApiError
     */
    public static deleteTypedTaskStateTasksTypedTasksStatesTypedTaskStateIdDelete(
        typedTaskStateId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/typed-tasks/states/{typed_task_state_id}',
            path: {
                'typed_task_state_id': typedTaskStateId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Typed Task State Period
     * @param typedTaskStateId
     * @param requestBody
     * @returns StatePeriod Successful Response
     * @throws ApiError
     */
    public static createTypedTaskStatePeriodTasksTypedTasksStatesTypedTaskStateIdPeriodPut(
        typedTaskStateId: string,
        requestBody: StatePeriod,
    ): CancelablePromise<StatePeriod> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/tasks/typed-tasks/states/{typed_task_state_id}/period',
            path: {
                'typed_task_state_id': typedTaskStateId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Typed Task State Period
     * @param typedTaskStateId
     * @returns void
     * @throws ApiError
     */
    public static deleteTypedTaskStatePeriodTasksTypedTasksStatesTypedTaskStateIdPeriodDelete(
        typedTaskStateId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/typed-tasks/states/{typed_task_state_id}/period',
            path: {
                'typed_task_state_id': typedTaskStateId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
