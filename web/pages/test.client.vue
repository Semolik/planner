<script>
import { faker } from "@faker-js/faker";

let uid = 0;

function generateItem() {
    return {
        name: faker.person.fullName(),
        avatar: faker.image.avatar(),
    };
}

function getData(count, letters) {
    const raw = {};

    const alphabet = "abcdefghijklmnopqrstuvwxyz".split("");

    for (const l of alphabet) {
        raw[l] = [];
    }

    for (let i = 0; i < count; i++) {
        const item = generateItem();
        const letter = item.name.charAt(0).toLowerCase();
        raw[letter].push(item);
    }

    const list = [];
    let index = 1;

    for (const l of alphabet) {
        raw[l] = raw[l].sort((a, b) => (a.name < b.name ? -1 : 1));
        if (letters) {
            list.push({
                id: uid++,
                index: index++,
                type: "letter",
                value: l,
                height: 200,
            });
        }
        for (const item of raw[l]) {
            list.push({
                id: uid++,
                index: index++,
                type: "person",
                value: item,
                height: 50,
            });
        }
    }

    return list;
}

export default {
    data() {
        return {
            list: [],
            gridItems: 6,
            scrollTo: 500,
        };
    },

    mounted() {
        this.list = getData(5000);
    },
};
</script>

<template>
    <div class="wrapper">
        <div class="toolbar">
            <label>
                Grid items per row
                <input
                    v-model.number="gridItems"
                    type="number"
                    min="2"
                    max="20"
                />
            </label>
            <input v-model.number="gridItems" type="range" min="2" max="20" />
            <span>
                <button @mousedown="$refs.scroller.scrollToItem(scrollTo)">
                    Scroll To:
                </button>
                <input
                    v-model.number="scrollTo"
                    type="number"
                    min="0"
                    :max="list.length - 1"
                />
            </span>
        </div>

        <RecycleScroller
            ref="scroller"
            class="scroller"
            :items="list"
            :item-size="128"
            :grid-items="gridItems"
            :item-secondary-size="100"
        >
            <template #default="{ item, index }">
                <div class="item">
                    <img :key="item.id" :src="item.value.avatar" />
                    <div class="index">
                        {{ index }}
                    </div>
                </div>
            </template>
        </RecycleScroller>
    </div>
</template>

<style scoped>
.wrapper,
.scroller {
    height: 400px;
}

.wrapper {
    display: flex;
    flex-direction: column;
}

.toolbar {
    flex: none;
}

.scroller {
    flex: 1;
}

.scroller :deep(.hover) img {
    opacity: 0.5;
}

.item {
    position: relative;
    height: 100%;
}

.index {
    position: absolute;
    top: 2px;
    left: 2px;
    padding: 4px;
    border-radius: 4px;
    background-color: rgba(255, 255, 255, 0.85);
    color: black;
}

img {
    width: 100%;
    height: 100%;
    background: #eee;
    object-fit: cover;
}
</style>
