<script lang="ts" setup>
interface RouteParams {
  id: string;
}

const route = useRoute()
const userId = (route.params as RouteParams).id
</script>

<template>
  <div>
    123
    User {{ userId }}
    <Base />
  </div>
</template>


