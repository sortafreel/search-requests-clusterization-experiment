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
const testPhrases = ['dog', 'cat', 'elephant', 'dingo']

const groupPhrases = async () => {
  store.phrases = testPhrases
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
            {{ store.phrases }}<br>
            <v-btn prepend-icon="$vuetify" @click="groupPhrases">
              Group phrases
            </v-btn><br><br>
            {{ store.groups}}<br><br>
            {{ store.singles }}
          </v-col>
          <v-col>
            <v-data-table :items="items"></v-data-table>
          </v-col>
          <v-col>
            <v-table>
              <thead>
              <tr>
                <th class="text-left">
                  Name
                </th>
                <th class="text-left">
                  Species
                </th>
              </tr>
              </thead>
              <tbody>
              <tr
                v-for="item in items"
                :key="item.name"
              >
                <td>{{ item.name }}</td>
                <td>{{ item.species }}</td>
              </tr>
              </tbody>
            </v-table>
          </v-col>
        </v-row>
      </v-container>


    </v-main>
  </v-app>
</template>
