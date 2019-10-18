#!/usr/bin/env ruby

# This script aggregates and cleans data from this dataset:
# http://en.openei.org/datasets/dataset/commercial-and-residential-hourly-load-profiles-for-all-tmy3-locations-in-the-united-states

def organise_data
  # Single big csv file where we want to aggregate all data
  outfile = File.open('energy-consumption.csv', 'w')

  # Columns we want to have in the output file:
  # * category = {commercial, residential}
  # * type = {restaurant, hospital, retail, etc.}
  # * name = name of the building (generally just the city where it is located)
  # * date = date of the year
  # * time = time of the day (hour by hour)
  # * energy = measured energy consuption for that date and hour
  outfile.puts('category,type,name,date,time,energy')
  
  rw_commercial_buildings_data(outfile)
  rw_residential_buildings_data(outfile)
  
  outfile.close
end

def rw_commercial_buildings_data(outfile)
  Dir.glob('commercial-buildings/*.csv') do |filename|
    # We scan commercial buildings first
    category = 'commercial'
    
    # We can get type and name from the filename
    type, name = filename.scan(/.*Bldg(.*)New2004.*USA\_(.*)\.csv/).first
    
    # Read and write the individual lines with the measurements
    rw_values(category, type, name, filename, outfile)
  end
end

def rw_residential_buildings_data(outfile)
  Dir.glob('residential-buildings/*.csv') do |filename|
    # We scan residential buildings next
    category = 'residential'
    
    # There are no subtypes for residential buildings
    type = 'residential'
    
    name = filename.scan(/USA\_(.*)\.[79].*\.csv/).first
    
    unless name
      puts "Filename: #{filename}"
      throw "Found a non-conformant filename"
    end
    
    name = name.first
    name.gsub!(/\./, '_') # Replace dots with underscores
    
    # Read and write the individual lines with the measurements
    rw_values(category, type, name, filename, outfile)
  end
end

# Read date, time, and energy measurement from the individual csv file
# and writes them to the output csv file
def rw_values(category, type, name, filename, outfile)
  first_line = true
  File.readlines(filename).each do |line|
    # Skip the first line, as it contains the header
    if first_line
      first_line = false
      next
    end
    
    # Split the line by commas
    fields = line.split(',')
    
    # Check that the csv is conformant to the format
    if fields.size < 9
      puts "Malformed line: #{line}"
      puts "In file: #{filename}"
      throw "Expecting at least 9 fields in commercial building csv files"
    end
    
    datetime = fields[0]
    energy = fields[1]
    
    # Parse the first column (datetime)
    month, day, hour = datetime.scan(/(\d\d)\/(\d\d)\s*(\d\d)/).first
    
    # In the original csv hours are 01-24, we convert it to 00-23
    hour = (hour.to_i - 1).to_s.rjust(2, '0')
    
    # We know the data is relative to 2004
    date = "2004-#{month}-#{day}"
    time = "#{hour}:00"
    
    # Write the extracted data to the output csv
    outfile.puts("#{category},#{type},#{name},#{date},#{time},#{energy}")
  end
end

organise_data
