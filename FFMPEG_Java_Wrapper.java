//import necessary libraries
import java.io.File;
import java.io.IOException;

//FFMPEG_Java_Wrapper class
public class FFMPEG_Java_Wrapper {

    //main
    public static void main(String[] args) {

        //try block
        try {
            //create process
            Runtime rt = Runtime.getRuntime();
            //save the location
            File folder = new File("/home/raz/Downloads/mal_mp4/new");
            //save all files in an array that are retrieved from the specified folder
            File[] file = folder.listFiles();
            System.out.println(file);
            /*
            for each filename, open the command prompt
            and execute the specified command.
             */
            for (int i = 0; i < file.length; i++) {
                String sentences = file[i].getName().substring(0, (file[i].getName().length()) - 4);
                String str=sentences+ ".avi ";
                System.out.println(str);
                rt.exec("ffmpeg -i " + file[i].getName()
                        +" "+ str , null, folder);
            }//end for
        } //end try
        catch (IOException e) {
            System.out.println(e);
        }//end catch

    }//end main
}//end FFMPEG_Java_Wrapper