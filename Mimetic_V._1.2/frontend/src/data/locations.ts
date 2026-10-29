import { Country, State } from 'country-state-city'

export interface LocationOption {
  name: string
  code: string
}

export function getAllCountries(): LocationOption[] {
  return Country.getAllCountries()
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(c => ({ name: c.name, code: c.isoCode }))
}

export function getDepartments(countryCode: string): LocationOption[] {
  return State.getStatesOfCountry(countryCode)
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(s => ({ name: s.name, code: s.isoCode }))
}

export async function getCities(countryCode: string, stateCode: string): Promise<LocationOption[]> {
  const { City } = await import('country-state-city')
  return City.getCitiesOfState(countryCode, stateCode)
    .slice()
    .sort((a, b) => a.name.localeCompare(b.name))
    .map(c => ({ name: c.name, code: `${c.countryCode}-${c.stateCode}-${c.name}` }))
}