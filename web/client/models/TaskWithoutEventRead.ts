/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { TypedTaskRead } from './TypedTaskRead';
export type TaskWithoutEventRead = {
    event_id?: (string | null);
    name: string;
    id: string;
    typed_tasks: Array<TypedTaskRead>;
};

