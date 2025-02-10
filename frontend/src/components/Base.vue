<script lang="ts" setup>
import { ref } from 'vue'
import { useClusterizerStore } from '@/stores/clusterizer'

const drawer = ref<boolean>(false)
const store = useClusterizerStore()
const items = [
  {
    name: 'African Elephant',
    species: 'Loxodonta africana',
    diet: 'Herbivore',
    habitat: 'Savanna, Forests'
  },
  {
    name: 'African Wild Dog',
    species: 'Lycaon pictus',
    diet: 'Carnivore',
    habitat: 'Savanna'
  },
  {
    name: 'African Lion',
    species: 'Panthera leo',
    diet: 'Carnivore',
    habitat: 'Savanna'
  },
  {
    name: 'African Penguin',
    species: 'Spheniscus demersus',
    diet: 'Carnivore',
    habitat: 'Coastal'
  },
  {
    name: 'African Rock Python',
    species: 'Python sebae',
    diet: 'Carnivore',
    habitat: 'Savanna, Forests'
  },
  {
    name: 'African Spurred Tortoise',
    species: 'Centrochelys sulcata',
    diet: 'Herbivore',
    habitat: 'Desert'
  }
]
const inputPhrases = ref<string>('')

const groupPhrases = async () => {
  // Split input phrases by ','
  store.phrases = inputPhrases.value.split(',').map(phrase => phrase.trim())
  await store.requestGroupPhrases()
}

</script>


<template>
  <v-app id="inspire">
    <v-navigation-drawer v-model="drawer">
      <!--  -->
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

      <v-app-bar-title>Application</v-app-bar-title>
    </v-app-bar>

    <v-main>
      <v-container>
        <v-row>
          <v-col
            cols="12"
            sm="4"
          >
            <v-progress-linear color="blue-lighten-3" indeterminate :height="7"
                               v-if="store.loading"></v-progress-linear>
            <v-form>
              <v-container fluid>
                <v-row>
                  <v-col
                    cols="12"
                  >
                    <v-textarea label="Phrases" v-model="inputPhrases"></v-textarea>
                  </v-col>
                </v-row>
              </v-container>
            </v-form>

            {{ store.phrases }}<br>
            <v-btn prepend-icon="$vuetify" @click="groupPhrases">
              Group phrases
            </v-btn>
            <br><br>
            {{ store.groups }}<br><br>
            {{ store.singles }}
          </v-col>
          <v-col>
            <v-table v-if="store.singles.length && !store.loading">
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
            <v-table v-if="Object.keys(store.groups).length && !store.loading">
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
