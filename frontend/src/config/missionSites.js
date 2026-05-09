import thumbOfficial from '@/assets/mission-sites/official-zombicide.svg'
import thumbMissionsFr from '@/assets/mission-sites/missions-fr.svg'
import thumbCompendium from '@/assets/mission-sites/boardgame-compendium.svg'
import thumbEren from '@/assets/mission-sites/eren-histarion.svg'

/** Liens externes vers des banques de missions PDF (fan sites et officiel). */
export const MISSION_SITE_ENTRIES = [
  {
    id: 'official',
    url: 'https://www.zombicide.com/classic-missions/',
    thumb: thumbOfficial
  },
  {
    id: 'missionsFr',
    url: 'http://zombicide-missions.fr/?tileset=ALL',
    thumb: thumbMissionsFr
  },
  {
    id: 'compendium',
    url: 'https://boardgamecompendium.com/fr/missions.php?game=black-plague',
    thumb: thumbCompendium
  },
  {
    id: 'erenHistarion',
    url: 'https://zombicide.eren-histarion.fr/missions/',
    thumb: thumbEren
  }
]
