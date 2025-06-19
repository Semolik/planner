/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_add_file_to_home_note_home_notes__note_id__files_post } from '../models/Body_add_file_to_home_note_home_notes__note_id__files_post';
import type { Body_create_home_note_home_notes_post } from '../models/Body_create_home_note_home_notes_post';
import type { Body_update_home_note_home_notes__note_id__put } from '../models/Body_update_home_note_home_notes__note_id__put';
import type { File } from '../models/File';
import type { HomeNoteRead } from '../models/HomeNoteRead';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class HomeService {
    /**
     * Get Home Notes
     * Получить заметки для главной страницы.
     * @returns HomeNoteRead Successful Response
     * @throws ApiError
     */
    public static getHomeNotesHomeNotesGet(): CancelablePromise<Array<HomeNoteRead>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/home/notes',
        });
    }
    /**
     * Create Home Note
     * @param formData
     * @returns HomeNoteRead Successful Response
     * @throws ApiError
     */
    public static createHomeNoteHomeNotesPost(
        formData: Body_create_home_note_home_notes_post,
    ): CancelablePromise<HomeNoteRead> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/home/notes',
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Update Home Note
     * Обновить заметку для главной страницы.
     * @param noteId
     * @param formData
     * @returns HomeNoteRead Successful Response
     * @throws ApiError
     */
    public static updateHomeNoteHomeNotesNoteIdPut(
        noteId: string,
        formData: Body_update_home_note_home_notes__note_id__put,
    ): CancelablePromise<HomeNoteRead> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/home/notes/{note_id}',
            path: {
                'note_id': noteId,
            },
            formData: formData,
            mediaType: 'application/x-www-form-urlencoded',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete Home Note
     * Удалить заметку для главной страницы.
     * @param noteId
     * @returns void
     * @throws ApiError
     */
    public static deleteHomeNoteHomeNotesNoteIdDelete(
        noteId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/home/notes/{note_id}',
            path: {
                'note_id': noteId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Add File To Home Note
     * @param noteId
     * @param formData
     * @returns File Successful Response
     * @throws ApiError
     */
    public static addFileToHomeNoteHomeNotesNoteIdFilesPost(
        noteId: string,
        formData: Body_add_file_to_home_note_home_notes__note_id__files_post,
    ): CancelablePromise<File> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/home/notes/{note_id}/files',
            path: {
                'note_id': noteId,
            },
            formData: formData,
            mediaType: 'multipart/form-data',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Delete File From Home Note
     * Удалить файл из заметки для главной страницы.
     * @param noteId
     * @param fileId
     * @returns void
     * @throws ApiError
     */
    public static deleteFileFromHomeNoteHomeNotesNoteIdFilesFileIdDelete(
        noteId: string,
        fileId: string,
    ): CancelablePromise<void> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/home/notes/{note_id}/files/{file_id}',
            path: {
                'note_id': noteId,
                'file_id': fileId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
