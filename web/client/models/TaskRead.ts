/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventRead } from './EventRead';
import type { TypedTaskRead } from './TypedTaskRead';
export type TaskRead = {
    event_id?: (string | null);
    name: string;
    id: string;
    event: EventRead;
    typed_tasks: Array<TypedTaskRead>;
};

