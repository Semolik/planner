/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_upload_file_to_task_tasks__task_id__files_post } from '../models/Body_upload_file_to_task_tasks__task_id__files_post';
import type { Body_upload_image_to_task_tasks__task_id__images_post } from '../models/Body_upload_image_to_task_tasks__task_id__images_post';
import type { CreateTypedTask } from '../models/CreateTypedTask';
import type { File } from '../models/File';
import type { ImageInfo } from '../models/ImageInfo';
import type { TaskCreate } from '../models/TaskCreate';
import type { TaskRead } from '../models/TaskRead';
import type { TypedTaskReadFull } from '../models/TypedTaskReadFull';
import type { UserRole } from '../models/UserRole';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class TasksService {
    /**
     * Get Tasks
     * @param page
     * @param hideBusyTasks
     * @param prioritizeUnassigned
     * @param token
     * @returns TaskRead Successful Response
     * @throws ApiError
     */
    public static getTasksTasksGet(
        page: number = 1,
        hideBusyTasks: boolean = true,
        prioritizeUnassigned: boolean = true,
        token?: (string | null),
    ): CancelablePromise<Array<TaskRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks',
            headers: {
                'token': token,
            },
            query: {
                'page': page,
                'hide_busy_tasks': hideBusyTasks,
                'prioritize_unassigned': prioritizeUnassigned,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Task
     * @param requestBody
     * @returns TaskRead Successful Response
     * @throws ApiError
     */
    public static createTaskTasksPost(
        requestBody: TaskCreate,
    ): CancelablePromise<TaskRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Tasks Token
     * @returns string Successful Response
     * @throws ApiError
     */
    public static getTasksTokenTasksTokenGet(): CancelablePromise<Record<string, string>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/token',
        });
    }
    /**
     * Set Tasks Token
     * @param role
     * @returns string Successful Response
     * @throws ApiError
     */
    public static setTasksTokenTasksTokenPut(
        role: UserRole,
    ): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/tasks/token',
            query: {
                'role': role,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Task By Id
     * @param taskId
     * @returns TaskRead Successful Response
     * @throws ApiError
     */
    public static getTaskByIdTasksTaskIdGet(
        taskId: string,
    ): CancelablePromise<TaskRead> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tasks/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Task
     * @param taskId
     * @returns void
     * @throws ApiError
     */
    public static deleteTaskTasksTaskIdDelete(
        taskId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/{task_id}',
            path: {
                'task_id': taskId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Create Typed Task
     * @param taskId
     * @param requestBody
     * @returns TypedTaskReadFull Successful Response
     * @throws ApiError
     */
    public static createTypedTaskTasksTaskIdTypedTasksPost(
        taskId: string,
        requestBody: CreateTypedTask,
    ): CancelablePromise<TypedTaskReadFull> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/{task_id}/typed-tasks',
            path: {
                'task_id': taskId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload File To Task
     * @param taskId
     * @param formData
     * @returns File Successful Response
     * @throws ApiError
     */
    public static uploadFileToTaskTasksTaskIdFilesPost(
        taskId: string,
        formData: Body_upload_file_to_task_tasks__task_id__files_post,
    ): CancelablePromise<File> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/{task_id}/files',
            path: {
                'task_id': taskId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Upload Image To Task
     * @param taskId
     * @param formData
     * @returns ImageInfo Successful Response
     * @throws ApiError
     */
    public static uploadImageToTaskTasksTaskIdImagesPost(
        taskId: string,
        formData: Body_upload_image_to_task_tasks__task_id__images_post,
    ): CancelablePromise<ImageInfo> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tasks/{task_id}/images',
            path: {
                'task_id': taskId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Image From Task
     * @param taskId
     * @param imageId
     * @returns void
     * @throws ApiError
     */
    public static deleteImageFromTaskTasksTaskIdImagesImageIdDelete(
        taskId: string,
        imageId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/{task_id}/images/{image_id}',
            path: {
                'task_id': taskId,
                'image_id': imageId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete File From Task
     * @param taskId
     * @param fileId
     * @returns void
     * @throws ApiError
     */
    public static deleteFileFromTaskTasksTaskIdFilesFileIdDelete(
        taskId: string,
        fileId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/tasks/{task_id}/files/{file_id}',
            path: {
                'task_id': taskId,
                'file_id': fileId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
