export interface PhrasesGroup {
  phrases: string[]; // Phrases in the group.
  avg_distance: number | null; // Average distance between phrases in the group.
}

export interface GroupingPhrasesOutput {
  groups: { [key: string]: PhrasesGroup }; // Grouped phrases.
  singles: string[]; // Phrases that weren't grouped.
}
