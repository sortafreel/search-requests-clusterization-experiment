<script lang="ts" setup>
import { ref } from 'vue'
import { useClusterizerStore } from '@/stores/clusterizer'

const store = useClusterizerStore()
const inputPhrases = ref<string>('')

const groupPhrases = async () => {
  // Split input phrases by ','
  store.phrases = inputPhrases.value.split(',').map(phrase => phrase.trim())
  await store.requestGroupPhrases()
}

</script>


<template>
  <v-app id="inspire">

    <v-app-bar>
      <v-app-bar-title>Application</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <v-row>
          <v-col
            cols="12"
            sm="4"
          >
            <v-progress-linear color="blue-lighten-3" indeterminate :height="7"
                               v-if="store.loading"></v-progress-linear>
            <v-form>
              <v-textarea label="Phrases (comma-separated)" v-model="inputPhrases"></v-textarea>
            </v-form>

            <v-btn prepend-icon="$vuetify" @click="groupPhrases">
              Group phrases
            </v-btn>
          </v-col>
          <v-col>
            <v-table>
              <thead>
              <tr>
                <th class="text-left">
                  Phrase
                </th>
              </tr>
              </thead>
              <tbody>
              <tr v-for="phrase in store.singles" :key="phrase">
                <td>{{ phrase }}</td>
              </tr>
              </tbody>
            </v-table>
          </v-col>
          <v-col>
            <v-table>
              <thead>
              <tr>
                <th class="text-left">
                  Group ID
                </th>
                <th class="text-left">
                  Phrases
                </th>
                <th class="text-left">
                  AVG distance
                </th>
              </tr>
              </thead>
              <tbody>
              <template v-for="[groupKey, group] in Object.entries(store.groups)"
                        :key="groupKey">
                <tr v-for="phrase in group.phrases" :key="phrase">
                  <td>{{ groupKey }}</td>
                  <td>{{ phrase }}</td>
                  <td>{{ group.avg_distance }}</td>
                </tr>
              </template>
              </tbody>
            </v-table>
          </v-col>
        </v-row>
      </v-container>


    </v-main>
  </v-app>
</template>
