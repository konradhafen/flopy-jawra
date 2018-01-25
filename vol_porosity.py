import os
import numpy as np
from osgeo import gdal
import csv

bratCaps = ['05', '25', '50', '100']

for bratCap in bratCaps:
    modelDir = "03_out_" + bratCap
    modDir = "MODFLOW_" + bratCap
    huc8 = str(16010202)
    path = r'E:\konrad\Projects\Modeling\BeaverWaterStorage\wrk_Data\AnalysisRuns\BearRiverHUC8/'+ huc8 + '/HUC12'
    outfile = r'E:\konrad\Projects\Modeling\BeaverWaterStorage\wrk_Data\AnalysisRuns\BearRiverHUC8/'+ huc8 + '/OverallResults' + '/' + modDir + '_por.csv'
    inDir = "02_rasIn"
    os.chdir(path)
    ofile = open(outfile, 'wb')
    writer = csv.writer(ofile)
    row = ["huc12", "brat_cap","gw_lo_por", "gw_mid_por", "gw_hi_por"]
    writer.writerow(row)

    for subdir, dirs, files in os.walk(path):
        if os.path.exists(subdir + "/" + modDir + "/hdch_mid.tif") and (os.path.relpath(subdir,path)) != '160102040505':
            print subdir + " running " + os.path.relpath(subdir, path)
            os.chdir(subdir)

            porDs = gdal.Open(inDir + "/por_vbfac.tif")
            geot = porDs.GetGeoTransform()
            hdloDS = gdal.Open(modDir + '/hdch_lo.tif')
            hdmidDS = gdal.Open(modDir + '/hdch_mid.tif')
            hdhiDS = gdal.Open(modDir + '/hdch_hi.tif')
            porData = porDs.GetRasterBand(1).ReadAsArray()
            pnd = porDs.GetRasterBand(1).GetNoDataValue()
            porData[porData == pnd] = np.nan

            #volume for low dam height water table change
            hdlo = hdloDS.GetRasterBand(1).ReadAsArray()
            lond = hdloDS.GetRasterBand(1).GetNoDataValue()
            hdlo[hdlo == lond] = np.nan
            volLoPor = np.multiply(porData, hdlo)
            gwlo = np.nansum(volLoPor) * abs(geot[1]) * abs(geot[5])

            write2 = np.where(np.isnan(volLoPor), -9999.0, volLoPor)
            hdch_dslo = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_lo_por.tif', porDs.RasterXSize,
                                                             porDs.RasterYSize, 1, gdal.GDT_Float32)
            hdch_dslo.SetProjection(porDs.GetProjection())
            hdch_dslo.SetGeoTransform(geot)
            hdch_dslo.GetRasterBand(1).WriteArray(write2)
            hdch_dslo.GetRasterBand(1).FlushCache()
            hdch_dslo.GetRasterBand(1).SetNoDataValue(-9999.0)

            # volume for mid dam height water table change
            hdmid = hdmidDS.GetRasterBand(1).ReadAsArray()
            midnd = hdmidDS.GetRasterBand(1).GetNoDataValue()
            hdmid[hdmid == midnd] = np.nan
            volMidPor = np.multiply(porData, hdmid)
            gwmid = np.nansum(volMidPor) * abs(geot[1]) * abs(geot[5])

            write2 = np.where(np.isnan(volMidPor), -9999.0, volMidPor)
            hdch_dsmid = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_mid_por.tif', porDs.RasterXSize,
                                                             porDs.RasterYSize, 1, gdal.GDT_Float32)
            hdch_dsmid.SetProjection(porDs.GetProjection())
            hdch_dsmid.SetGeoTransform(geot)
            hdch_dsmid.GetRasterBand(1).WriteArray(write2)
            hdch_dsmid.GetRasterBand(1).FlushCache()
            hdch_dsmid.GetRasterBand(1).SetNoDataValue(-9999.0)

            # volume for high dam height water table change
            hdhi = hdhiDS.GetRasterBand(1).ReadAsArray()
            hind = hdhiDS.GetRasterBand(1).GetNoDataValue()
            hdhi[hdhi == hind] = np.nan
            volHiPor = np.multiply(porData, hdhi)
            gwhi = np.nansum(volHiPor) * abs(geot[1]) * abs(geot[5])

            write2 = np.where(np.isnan(volHiPor), -9999.0, volHiPor)
            hdch_dshi = gdal.GetDriverByName('GTiff').Create(modDir + '/hdch_hi_por.tif', porDs.RasterXSize,
                                                             porDs.RasterYSize, 1, gdal.GDT_Float32)
            hdch_dshi.SetProjection(porDs.GetProjection())
            hdch_dshi.SetGeoTransform(geot)
            hdch_dshi.GetRasterBand(1).WriteArray(write2)
            hdch_dshi.GetRasterBand(1).FlushCache()
            hdch_dshi.GetRasterBand(1).SetNoDataValue(-9999.0)

            row = [os.path.relpath(subdir, path), bratCap, gwlo, gwmid, gwhi]
            writer.writerow(row)

    ofile.close()