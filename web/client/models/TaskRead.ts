/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { EventGroupReadShort } from './EventGroupReadShort';
import type { EventRead } from './EventRead';
import type { File } from './File';
import type { ImageInfo } from './ImageInfo';
import type { TypedTaskRead } from './TypedTaskRead';
export type TaskRead = {
    event_id?: (string | null);
    name: string;
    use_in_pgas: boolean;
    id: string;
    all_typed_tasks_completed: boolean;
    event?: (EventRead | null);
    typed_tasks: Array<TypedTaskRead>;
    images: Array<ImageInfo>;
    files: Array<File>;
    group?: (EventGroupReadShort | null);
};

