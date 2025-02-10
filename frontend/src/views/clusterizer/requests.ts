import axios from '@axios'

export const requestGroupPhrasesAxios = async (
  phrases: string[]
) => {
  return axios
    .post(
      `/clusterizer/group/`,
      { phrases }
    )
}
