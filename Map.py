import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import sys, os
import pandas as pd
from matplotlib.animation import FuncAnimation
from matplotlib import animation



'''
This code should plot cool things. Kudos to this guy: http://maxberggren.se/2015/08/04/basemap/
'''

#Circle size
cs = 100

#The disasters we want to compute
disasters = ["2012_Colorado_wildfires", "2012_Costa_Rica_earthquake", "2012_Guatemala_earthquake", "2012_Italy_earthquakes",
             "2012_Philipinnes_floods", "2012_Typhoon_Pablo", "2012_Venezuela_refinery", "2013_Alberta_floods", 
             "2013_Australia_bushfire", "2013_Bohol_earthquake", "2013_Boston_bombings", "2013_Brazil_nightclub_fire"
             "2013_Colorado_floods", "2013_Glasgow_helicopter_crash", "2013_LA_airport_shootings", "2013_Lac_Megantic_train_crash",
             "2013_Manila_floods", "2013_NY_train_crash", "2013_Queensland_floods", "2013_Russia_meteor", "2013_Sardinia_floods",
             "2013_Savar_building_collapse", "2013_Singapore_haze", "2013_Spain_train_crash", "2013_Typhoon_Yolanda",
             "2013_West_Texas_explosion"]

#The longitudes and latitudes of those disasters, I have looked every disaster on
#wikipedia and Google Maps to look for the proper coordinates, this should be precise.
#Thank you the genious before me for Ctrl + C, Ctrl + V, you will not be forgotten
disasters_loc = [(-107.874087, 37.601603), (-85.369114, 10.190360), (-91.643023, 14.154038), (11.291664, 44.831569),
				(121.189056, 16.584973), (125.207126, 11.426647), (-70.240183, 11.779181), (-115.044637, 56.239523),
				(146.416648, -32.975678), (124.019033, 9.916166), (-71.074807, 42.349857), (-53.807350, -29.684646),
				(-104.402906, 40.746255), (-4.249913, 55.855828), (-118.407672, 33.941527), (-70.880163, 45.576103),
				(120.985920, 14.594341), (-73.921998, 40.878700), (152.354405, -24.864094), (61.389340, 55.155288), (9.499481, 40.925089),
				(90.272673, 23.870266), (103.895606, 1.303934), (-8.545034, 42.870051), (120.930126, 30.512670),
				(-97.088317, 31.815593)]

#The nice names of the disasters to be displayed
disasters_nn = ["Colorado wildfires", "Costa Rica earthquake", "Guatemala earthquake", "Italy earthquakes",
                "Philipinnes floods", "Typhoon Pablo", "Venezuela refinery", "Alberta floods",
                "Australia bushfire", "Bohol earthquake", "Boston bombings", "Brazil nightclub fire",
                "Colorado floods", "Glasgow helicopter crash", "LA airport shootings", "Lac Megantic train crash",
                "Manila floods", "NY train crash", "Queensland floods", "Russia meteor", "Sardinia floods",
                "Savar building collapse", "Singapore haze", "Spain train crash", "Typhoon Yolanda",
                "West Texas explosion"]

'''
This has been way harder than original intended.
'''
def animate(i):

	global general_sentiment
	global time_text
	global sphere
	global no_sentiment

	row_index = i + 1 
	row = df.ix[i + 1]

	general_sentiment += row["Sentiment"]

	#This is to remove the no sentimental tweets from the normalization
	if row["Sentiment"] == 0:
		no_sentiment -= 1

	print "Processing tweet", row_index, "of", df.shape[0]
	print "The sentiment for", disasters_nn[index], "is", general_sentiment/(row_index+1)
	
	#Transform coordinates to the plot
	x1, y1 = m(disasters_loc[index][0], disasters_loc[index][1]) 
	
	sphere.remove()

	#Maximum and minimum values for this disaster
	vmax_val = df.ix[df['Sentiment'].idxmax()]["Sentiment"]
	vmin_val = df.ix[df['Sentiment'].idxmin()]["Sentiment"]

	sphere =  m.scatter(x1, y1, 
	          s=100, 
	          marker="o", 
	          c=general_sentiment/(row_index + 1 - no_sentiment),
	          cmap=cm.jet,
			  vmin=vmin_val,
			  vmax=vmax_val,
	          zorder=10, 
	          alpha=0.8)

	#Set the time
	time_text.set_text(str(general_sentiment/(row_index+1)) + " " + row["Timestamp"])

	print "Updating"

for index, disaster in enumerate(disasters):

	if not os.path.exists("./Results/" + disaster):
		os.makedirs("./Results/" + disaster)

	#Is late, I am just assuming the files and the code are in the same directory
	df = pd.read_pickle(disaster + ' .p')
	df = df.sort_values("POSIX Timestamp")
	
	m = Basemap(resolution='c',
	            projection='kav7',
	            lat_0=0., # Center around
	            lon_0=0.) # lat 0, lon 0
	
	n_graticules = 18
	parallels = np.arange(-80., 90, n_graticules)
	meridians = np.arange(0., 360., n_graticules)
	lw = 1
	dashes = [5,7] # 5 dots, 7 spaces... repeat
	graticules_color = 'grey'
	
	fig1 = plt.figure(figsize=(32,40))
	fig1.patch.set_facecolor('#e6e8ec')
	ax = fig1.add_axes([0.1,0.1,0.8,0.8])
	
	m.drawmapboundary(color='white', 
	                  linewidth=0.0, 
	                  fill_color='white')
	m.drawparallels(parallels, 
	                linewidth=lw, 
	                dashes=dashes, 
	                color=graticules_color)
	m.drawmeridians(meridians, 
	                linewidth=lw, 
	                dashes=dashes, 
	                color=graticules_color)
	m.drawcoastlines(linewidth=0)
	m.fillcontinents('gray', 
	                 lake_color='white')
	m.drawcountries(linewidth=1, 
	                linestyle='solid', 
	                color='white', 
	                zorder=30)
	
	title = plt.title(disasters_nn[index], 
	                  fontsize=20)
	title.set_y(1.03) # Move the title a bit for niceness

	#First iteration
	global general_sentiment
	global time_text
	global sphere
	global no_sentiment

	no_sentiment      = 0
	general_sentiment = 0

	row_index = 0
	row = df.ix[0]

	general_sentiment += row["Sentiment"]

	#This is to remove the no sentimental tweets from the normalization
	if row["Sentiment"] == 0:
		no_sentiment -= 1

	print "Processing tweet", row_index, "of", df.shape[0]
	print "The sentiment for", disasters_nn[index], "is", general_sentiment/(row_index+1)
	
	#Transform coordinates to the plot
	x1, y1 = m(disasters_loc[index][0], disasters_loc[index][1]) 

	#Maximum and minimum values for this disaster
	vmax_val = df.ix[df['Sentiment'].idxmax()]["Sentiment"]
	vmin_val = df.ix[df['Sentiment'].idxmin()]["Sentiment"]

	sphere =  m.scatter(x1, y1, 
	          s=100, 
	          marker="o", 
	          c=general_sentiment/(row_index + 1 - no_sentiment),
	          cmap=cm.jet,
			  vmin=vmin_val,
			  vmax=vmax_val,
	          zorder=10, 
	          alpha=0.8)

	#Add the time
	time_text = ax.text(20, 6, str(general_sentiment) + " " + row["Timestamp"], fontsize=15)

	anim = FuncAnimation(
		fig1, animate, interval=2, frames=df.shape[0]-1, repeat=False)#)


	plt.rcParams['savefig.bbox'] = 'tight'

	#mywriter = animation.FFMpegWriter(fps=30, metadata=metadata, extra_args=['-vcodec', 'libx264'])
	#anim.save(disaster + '.mp4')#, dpi=100, writer=mywriter)
	#anim.save(disaster + '.gif', writer='imagemagick')
	plt.draw()
	plt.show(block=False)

	
		#fig1.savefig("./Results/" + disaster + "/" + disaster + "-" + str(row_index) + '.png', dpi=fig1.dpi, bbox_inches='tight')
		#plt.close()