import { defineStore } from 'pinia'
import { requestGroupPhrasesAxios } from '@/views/clusterizer/requests'
import type { GroupingPhrasesOutput, PhrasesGroup } from '@/views/clusterizer/types'

export const useClusterizerStore = defineStore('clusterizer', {
  state: () => ({
    loading: false as boolean,
    phrases: [] as string[],
    groups: {} as { [key: string]: PhrasesGroup },
    singles: [] as string[]
  }),
  actions: {
    async requestGroupPhrases() {
      this.loading = true
      await requestGroupPhrasesAxios(this.phrases).then((response) => {
        const responseData = response.data as GroupingPhrasesOutput
        this.groups = responseData.groups
        this.singles = responseData.singles
      }).catch(error => {
        console.error(`Error when grouping phrases: ${error}`)
      })
        .finally(() => {
          this.loading = false
        })
    }
  }
})
