/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { File } from './File';
import type { UserRole } from './UserRole';
export type HomeNoteRead = {
    id: string;
    text: string;
    files?: Array<File>;
    role: UserRole;
};

